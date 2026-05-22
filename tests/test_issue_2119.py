import pytest
import asyncio
from src.agent.executor import AgentExecutor

def test_executor_result_retention():
    async def run_test():
        executor = AgentExecutor(max_concurrent=5, max_results=3)
        async def handler(agent_id, task_data):
            return task_data["id"]

        exec_ids = []
        for i in range(5):
            eid = await executor.execute("agent-1", {"id": f"t-{i}"}, handler)
            exec_ids.append(eid)
            await asyncio.sleep(0.01)
            
        assert executor.get_result(exec_ids[0]) is None
        assert executor.get_result(exec_ids[1]) is None
        assert executor.get_result(exec_ids[2]) is not None
        assert executor.get_result(exec_ids[3]) is not None
        assert executor.get_result(exec_ids[4]) is not None

    asyncio.run(run_test())

def test_executor_result_ttl():
    async def run_test():
        executor = AgentExecutor(max_concurrent=5, result_ttl_seconds=0.05)
        async def handler(agent_id, task_data):
            return "ok"

        eid = await executor.execute("agent-1", {"id": "t-1"}, handler)
        assert executor.get_result(eid) is not None
        await asyncio.sleep(0.08)
        assert executor.get_result(eid) is None

    asyncio.run(run_test())
