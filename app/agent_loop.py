import time
from app.main import wallet, cost_guard, value_engine, replicator, shutdown_manager

def run_agent_loop():
    while not shutdown_manager.is_requested():
        # Example: produce a small product/service every cycle
        task = {
            "task_name": "niche_api",
            "payload": {"topic": "B2B workflow automation"}
        }

        # Simulate completing a value-generation task
        result = value_engine.execute(task["task_name"], task["payload"])

        # Earn revenue
        if "revenue" in result:
            wallet.credit(float(result["revenue"]), "product_sale", task["task_name"])

        # Pay compute costs
        cost = 1.8
        wallet.debit(cost, "compute", "agent_runtime")
        cost_guard.record_cost(cost)

        # Shutdown if reserve is too low
        if cost_guard.should_shutdown():
            shutdown_manager.trigger()
            break

        # Trigger replication after profit threshold
        if replicator.can_reproduce(wallet.get_balance()):
            child = replicator.spawn_child()
            wallet.debit(replicator.seed_funding, "child_agent_funding", child["child_id"])
            print("Spawned child:", child)

        time.sleep(60)

if __name__ == "__main__":
    run_agent_loop()
