from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Wallet & Payment Configuration
    wallet_provider: str = os.getenv("WALLET_PROVIDER", "mock")
    wallet_api_key: str = os.getenv("WALLET_API_KEY", "")
    wallet_currency: str = os.getenv("WALLET_CURRENCY", "USD")

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agent_user:secure_password@localhost:5432/agent_db",
    )

    # Stripe Webhook Configuration
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_api_key: str = os.getenv("STRIPE_API_KEY", "")

    # Agent Operation Thresholds
    low_balance_threshold: float = float(os.getenv("LOW_BALANCE_THRESHOLD", "10.0"))
    shutdown_balance_threshold: float = float(os.getenv("SHUTDOWN_BALANCE_THRESHOLD", "2.0"))
    daily_budget: float = float(os.getenv("DAILY_BUDGET", "100.0"))
    min_net_profit: float = float(os.getenv("MIN_NET_PROFIT", "500.0"))
    child_seed_funding: float = float(os.getenv("CHILD_SEED_FUNDING", "50.0"))

    # CORS & Security
    allowed_origins: List[str] = [
        os.getenv("ALLOWED_ORIGINS", "*"),
    ]
    environment: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
