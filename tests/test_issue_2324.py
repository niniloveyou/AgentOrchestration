import pytest
from src.sdk.decorators import task

def test_task_retries_validation():
    with pytest.raises(ValueError, match="Retries must be a non-negative integer"):
        @task(retries=-1)
        async def dummy_task():
            pass

    with pytest.raises(TypeError, match="Retries must be an integer"):
        @task(retries="invalid")
        async def dummy_task_string():
            pass
