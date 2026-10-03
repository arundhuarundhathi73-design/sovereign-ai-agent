import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from app.database import Base


class WalletModel(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    balance = Column(Float, default=100.0)
    currency = Column(String, default="USD")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'credit' or 'debit'
    recipient_or_source = Column(String, nullable=False)
    memo = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class TaskRecordModel(Base):
    __tablename__ = "tasks_history"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    task_name = Column(String, nullable=False)
    payload = Column(JSON, default={})
    revenue = Column(Float, default=0.0)
    status = Column(String, default="completed")  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
