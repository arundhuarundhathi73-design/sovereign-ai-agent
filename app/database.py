import os
import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://agent_user:secure_password@localhost:5432/agent_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WalletModel(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=100.0)
    currency = Column(String, default="USD")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
    return SessionLocal()
