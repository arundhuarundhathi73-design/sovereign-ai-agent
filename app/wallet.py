import os
from typing import Dict, Any, Optional

import requests


class WalletService:
    def __init__(self, provider: str, api_key: str, currency: str = "USD"):
        self.provider = provider.lower()
        self.api_key = api_key
        self.currency = currency
        self._balance = 100.0  # Fallback/initial balance

    def get_balance(self) -> float:
        if self.provider == "stripe" and self.api_key:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            try:
                response = requests.get(
                    "https://api.stripe.com/v1/balance",
                    headers=headers,
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    available = data.get("available", [])
                    if available:
                        amount = available[0].get("amount", self._balance)
                        return float(amount) / 100.0
            except Exception:
                pass
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
            "balance_after": self._balance,
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
            "balance_after": self._balance,
        }

    def create_payment_intent(self, amount: float, currency: str = "USD") -> Dict[str, Any]:
        """Example integration hook for a real payment rail like Stripe."""
        if self.provider != "stripe" or not self.api_key:
            return {
                "status": "mock_mode",
                "provider": self.provider,
                "amount": amount,
                "currency": currency,
                "message": "Stripe not configured; using fallback mock mode.",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "amount": int(amount * 100),
            "currency": currency.lower(),
            "payment_method_types[]": "card",
        }

        try:
            response = requests.post(
                "https://api.stripe.com/v1/payment_intents",
                headers=headers,
                data=data,
                timeout=5,
            )
            if response.status_code == 200:
                return response.json()
            return {
                "status": "error",
                "provider": "stripe",
                "message": response.text,
            }
        except Exception as exc:
            return {
                "status": "error",
                "provider": "stripe",
                "message": str(exc),
            }
