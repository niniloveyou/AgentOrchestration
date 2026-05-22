import pytest
from src.agent.executor import AgentExecutor

def test_executor_max_concurrent_validation():
    with pytest.raises(ValueError, match="max_concurrent must be a positive integer"):
        AgentExecutor(max_concurrent=0)
    with pytest.raises(ValueError, match="max_concurrent must be a positive integer"):
        AgentExecutor(max_concurrent=-5)
    with pytest.raises(TypeError, match="max_concurrent must be an integer"):
        AgentExecutor(max_concurrent="invalid")
