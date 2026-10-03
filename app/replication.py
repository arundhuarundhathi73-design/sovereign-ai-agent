from typing import Dict, Any

class ReplicationManager:
    def __init__(self, min_net_profit: float, seed_funding: float):
        self.min_net_profit = min_net_profit
        self.seed_funding = seed_funding

    def can_reproduce(self, wallet_balance: float) -> bool:
        # Net profit rule: must be above threshold and balanced.
        return wallet_balance >= self.min_net_profit

    def spawn_child(self) -> Dict[str, Any]:
        child_id = "child-agent-01"
        return {
            "status": "child_spawned",
            "child_id": child_id,
            "seed_funding": self.seed_funding,
            "plan": {
                "wallet_seed": self.seed_funding,
                "role": "autonomous_worker",
                "region": "us-east-1",
                "container": "agent-worker"
            }
        }
