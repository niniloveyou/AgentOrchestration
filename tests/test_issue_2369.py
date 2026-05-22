import pytest
import asyncio
from src.sdk.decorators import task

def test_sync_task_decorator_support():
    async def run_test():
        @task(name="sync-task", timeout=2)
        def sync_handler(val):
            return val + 10
            
        res = await sync_handler(5)
        assert res == 15
        assert sync_handler.__task_config__["name"] == "sync-task"

    asyncio.run(run_test())
