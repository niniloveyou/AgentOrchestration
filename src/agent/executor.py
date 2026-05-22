"""Agent Executor — Handles task execution within agent sandboxes."""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, List
from uuid import uuid4


class AgentExecutor:
    def __init__(self, max_concurrent: int = 5, max_results: Optional[int] = 100, result_ttl_seconds: Optional[float] = None):
        if not isinstance(max_concurrent, int):
            raise TypeError("max_concurrent must be an integer")
        if max_concurrent <= 0:
            raise ValueError("max_concurrent must be a positive integer")
            
        self.max_concurrent = max_concurrent
        self.max_results = max_results
        self.result_ttl_seconds = result_ttl_seconds
        
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, Any] = {}
        self._result_timestamps: Dict[str, float] = {}

    def _cleanup_results(self) -> None:
        now = time.time()
        # Clean by TTL
        if self.result_ttl_seconds is not None:
            expired = [exec_id for exec_id, ts in list(self._result_timestamps.items()) if now - ts > self.result_ttl_seconds]
            for exec_id in expired:
                self._results.pop(exec_id, None)
                self._result_timestamps.pop(exec_id, None)
        
        # Clean by max_results count
        if self.max_results is not None and len(self._results) > self.max_results:
            sorted_keys = sorted(self._result_timestamps.keys(), key=lambda k: self._result_timestamps[k])
            excess = len(self._results) - self.max_results
            for exec_id in sorted_keys[:excess]:
                self._results.pop(exec_id, None)
                self._result_timestamps.pop(exec_id, None)

    async def execute(self, agent_id: str, task: Dict[str, Any], handler: Callable) -> str:
        execution_id = str(uuid4())
        async with self._semaphore:
            task_obj = asyncio.create_task(
                self._run_execution(execution_id, agent_id, task, handler)
            )
            self._active_tasks[execution_id] = task_obj
            try:
                result = await task_obj
                self._results[execution_id] = result
                self._result_timestamps[execution_id] = time.time()
            except Exception as e:
                self._results[execution_id] = {"error": str(e)}
                self._result_timestamps[execution_id] = time.time()
            finally:
                self._active_tasks.pop(execution_id, None)
                self._cleanup_results()
        return execution_id

    async def _run_execution(self, exec_id: str, agent_id: str, task: Dict, handler: Callable) -> Any:
        start = time.time()
        result = await handler(agent_id, task)
        duration = time.time() - start
        return {
            "execution_id": exec_id,
            "agent_id": agent_id,
            "task_id": task.get("id"),
            "result": result,
            "duration": duration,
            "timestamp": time.time(),
        }

    def get_result(self, execution_id: str) -> Optional[Any]:
        self._cleanup_results()
        return self._results.get(execution_id)

    def cancel(self, execution_id: str) -> bool:
        task = self._active_tasks.get(execution_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    async def shutdown(self) -> None:
        for task in self._active_tasks.values():
            task.cancel()
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks.values(), return_exceptions=True)
