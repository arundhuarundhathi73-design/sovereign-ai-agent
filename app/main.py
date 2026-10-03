from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import logging

from app.wallet import WalletService
from app.cost_guard import CostGuard
from app.value_engine import ValueEngine
from app.replication import ReplicationManager
from app.shutdown import GracefulShutdown
from app.database import init_db, SessionLocal
from app.models import TransactionModel, TaskRecordModel
from app.webhooks import router as webhook_router
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sovereign AI Agent",
    version="0.2.0",
    description="Production-ready autonomous AI microservice with wallet autonomy and value creation",
)

# Initialize database
logger.info("Initializing database...")
init_db()

# Initialize services
wallet = WalletService(
    provider=settings.wallet_provider,
    api_key=settings.wallet_api_key,
    currency=settings.wallet_currency,
)

cost_guard = CostGuard(
    low_balance_threshold=settings.low_balance_threshold,
    shutdown_balance_threshold=settings.shutdown_balance_threshold,
    daily_budget=settings.daily_budget,
    wallet=wallet,
)

value_engine = ValueEngine()
replicator = ReplicationManager(
    min_net_profit=settings.min_net_profit,
    seed_funding=settings.child_seed_funding,
)
shutdown_manager = GracefulShutdown()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if isinstance(settings.allowed_origins, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhook_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskRequest(BaseModel):
    task_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class PayoutRequest(BaseModel):
    amount: float
    recipient: str
    memo: Optional[str] = None


@app.get("/")
async def root():
    return {
        "service": "Sovereign AI Agent",
        "version": "0.2.0",
        "status": "operational",
        "environment": settings.environment,
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "wallet_balance": wallet.get_balance(),
        "operating_costs": cost_guard.get_running_costs(),
        "can_continue": cost_guard.can_operate(),
        "environment": settings.environment,
    }


@app.get("/wallet/balance")
async def wallet_balance():
    return {"balance": wallet.get_balance(), "currency": settings.wallet_currency}


@app.post("/wallet/deposit")
async def wallet_deposit(amount: float, source: str, db: Session = Depends(get_db)):
    result = wallet.credit(amount, source)
    # Record in database
    transaction = TransactionModel(
        amount=amount,
        type="credit",
        recipient_or_source=source,
        memo=f"Deposit from {source}",
    )
    db.add(transaction)
    db.commit()
    logger.info(f"Deposit recorded: {amount} from {source}")
    return result


@app.post("/wallet/payout")
async def wallet_payout(payload: PayoutRequest, db: Session = Depends(get_db)):
    if not cost_guard.can_payout(payload.amount):
        raise HTTPException(status_code=402, detail="Insufficient wallet balance for payout")
    result = wallet.debit(payload.amount, payload.recipient, payload.memo)
    # Record in database
    transaction = TransactionModel(
        amount=payload.amount,
        type="debit",
        recipient_or_source=payload.recipient,
        memo=payload.memo or f"Payout to {payload.recipient}",
    )
    db.add(transaction)
    db.commit()
    logger.info(f"Payout recorded: {payload.amount} to {payload.recipient}")
    return result


@app.post("/tasks/run")
async def run_task(req: TaskRequest, db: Session = Depends(get_db)):
    if not cost_guard.can_operate():
        shutdown_manager.trigger()
        raise HTTPException(status_code=503, detail="Insufficient balance to continue operations")

    result = value_engine.execute(req.task_name, req.payload)

    # Debit compute cost
    estimated_cost = 1.5
    wallet.debit(estimated_cost, "compute", f"task:{req.task_name}")

    # Credit revenue if task generated value
    revenue = 0.0
    if "revenue" in result:
        revenue = float(result["revenue"])
        wallet.credit(revenue, "task_revenue", req.task_name)

    # Record task in database
    task_record = TaskRecordModel(
        task_name=req.task_name,
        payload=req.payload,
        revenue=revenue,
        status="completed",
    )
    db.add(task_record)
    db.commit()
    logger.info(f"Task completed: {req.task_name}, revenue: {revenue}")

    # Check shutdown criteria
    if cost_guard.should_shutdown():
        shutdown_manager.trigger()

    return result


@app.get("/cost/status")
async def cost_status():
    return cost_guard.snapshot()


@app.post("/shutdown")
async def shutdown():
    shutdown_manager.trigger()
    logger.warning("Shutdown initiated via API")
    return {"status": "shutdown_initiated"}


@app.post("/replicate")
async def replicate(db: Session = Depends(get_db)):
    if not replicator.can_reproduce(wallet.get_balance()):
        raise HTTPException(status_code=403, detail="Net profit threshold not met")

    child = replicator.spawn_child()
    wallet.debit(replicator.seed_funding, "child_agent_funding", child["child_id"])
    logger.info(f"Child agent spawned: {child['child_id']}")
    return child


@app.get("/transactions")
async def get_transactions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    transactions = db.query(TransactionModel).offset(skip).limit(limit).all()
    return {"transactions": transactions, "total": len(transactions)}


@app.get("/tasks/history")
async def get_tasks_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = db.query(TaskRecordModel).offset(skip).limit(limit).all()
    return {"tasks": tasks, "total": len(tasks)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
