from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os

from app.wallet import WalletService
from app.cost_guard import CostGuard
from app.value_engine import ValueEngine
from app.replication import ReplicationManager
from app.shutdown import GracefulShutdown
from app.database import init_db

app = FastAPI(title="Sovereign AI Agent", version="0.1.0")

# Initialize database tables at startup.
init_db()

wallet = WalletService(
    provider=os.getenv("WALLET_PROVIDER", "mock"),
    api_key=os.getenv("WALLET_API_KEY", ""),
    currency=os.getenv("WALLET_CURRENCY", "USD"),
)

cost_guard = CostGuard(
    low_balance_threshold=float(os.getenv("LOW_BALANCE_THRESHOLD", "10.0")),
    shutdown_balance_threshold=float(os.getenv("SHUTDOWN_BALANCE_THRESHOLD", "2.0")),
    daily_budget=float(os.getenv("DAILY_BUDGET", "100.0")),
    wallet=wallet,
)

value_engine = ValueEngine()
replicator = ReplicationManager(
    min_net_profit=float(os.getenv("MIN_NET_PROFIT", "500.0")),
    seed_funding=float(os.getenv("CHILD_SEED_FUNDING", "50.0")),
)
shutdown_manager = GracefulShutdown()


class TaskRequest(BaseModel):
    task_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class PayoutRequest(BaseModel):
    amount: float
    recipient: str
    memo: Optional[str] = None


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "wallet_balance": wallet.get_balance(),
        "operating_costs": cost_guard.get_running_costs(),
        "can_continue": cost_guard.can_operate(),
    }


@app.get("/wallet/balance")
async def wallet_balance():
    return {"balance": wallet.get_balance()}


@app.post("/wallet/deposit")
async def wallet_deposit(amount: float, source: str):
    return wallet.credit(amount, source)


@app.post("/wallet/payout")
async def wallet_payout(payload: PayoutRequest):
    if not cost_guard.can_payout(payload.amount):
        raise HTTPException(status_code=402, detail="Insufficient wallet balance for payout")
    return wallet.debit(payload.amount, payload.recipient, payload.memo)


@app.post("/tasks/run")
async def run_task(req: TaskRequest):
    if not cost_guard.can_operate():
        shutdown_manager.trigger()
        raise HTTPException(status_code=503, detail="Insufficient balance to continue operations")

    result = value_engine.execute(req.task_name, req.payload)

    estimated_cost = 1.5
    wallet.debit(estimated_cost, "compute", f"task:{req.task_name}")

    if "revenue" in result:
        wallet.credit(float(result["revenue"]), "task_revenue", req.task_name)

    if cost_guard.should_shutdown():
        shutdown_manager.trigger()

    return result


@app.get("/cost/status")
async def cost_status():
    return cost_guard.snapshot()


@app.post("/shutdown")
async def shutdown():
    shutdown_manager.trigger()
    return {"status": "shutdown_initiated"}


@app.post("/replicate")
async def replicate():
    if not replicator.can_reproduce(wallet.get_balance()):
        raise HTTPException(status_code=403, detail="Net profit threshold not met")

    child = replicator.spawn_child()
    wallet.debit(replicator.seed_funding, "child_agent_funding", child["child_id"])
    return child


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
