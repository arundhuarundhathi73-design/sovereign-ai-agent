from typing import Dict, Any
from app.wallet import WalletService

class CostGuard:
    def __init__(self, low_balance_threshold: float, shutdown_balance_threshold: float,
                 daily_budget: float, wallet: WalletService):
        self.low_balance_threshold = low_balance_threshold
        self.shutdown_balance_threshold = shutdown_balance_threshold
        self.daily_budget = daily_budget
        self.wallet = wallet
        self.running_costs = 0.0

    def record_cost(self, amount: float):
        self.running_costs += amount

    def get_running_costs(self) -> float:
        return self.running_costs

    def can_operate(self) -> bool:
        balance = self.wallet.get_balance()
        return balance > self.low_balance_threshold

    def can_payout(self, amount: float) -> bool:
        return self.wallet.get_balance() >= amount + self.shutdown_balance_threshold

    def should_shutdown(self) -> bool:
        balance = self.wallet.get_balance()
        return balance <= self.shutdown_balance_threshold

    def snapshot(self) -> Dict[str, Any]:
        return {
            "balance": self.wallet.get_balance(),
            "running_costs": self.running_costs,
            "low_balance_threshold": self.low_balance_threshold,
            "shutdown_balance_threshold": self.shutdown_balance_threshold,
            "daily_budget": self.daily_budget,
            "can_operate": self.can_operate()
        }
