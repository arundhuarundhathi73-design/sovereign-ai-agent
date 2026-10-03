from typing import Dict, Any, Optional
import os

class WalletService:
    def __init__(self, provider: str, api_key: str, currency: str = "USD"):
        self.provider = provider
        self.api_key = api_key
        self.currency = currency
        self._balance = 100.0  # Seed starting balance for starter/demo

    def get_balance(self) -> float:
        # In production this hits a secure wallet provider API.
        return self._balance

    def credit(self, amount: float, source: str, memo: Optional[str] = None) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        self._balance += amount
        return {
            "status": "credited",
            "amount": amount,
            "currency": self.currency,
            "source": source,
            "memo": memo,
            "balance_after": self._balance
        }

    def debit(self, amount: float, recipient: str, memo: Optional[str] = None) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        if self._balance < amount:
            raise ValueError("Insufficient balance")
        self._balance -= amount
        return {
            "status": "debited",
            "amount": amount,
            "currency": self.currency,
            "recipient": recipient,
            "memo": memo,
            "balance_after": self._balance
        }
