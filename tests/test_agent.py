import pytest
from src.sdk.agent import BaseAgent
from typing import Any, Dict


class MockAgent(BaseAgent):
    async def setup(self) -> None:
        pass

    async def handle_task(self, task: Dict[str, Any]) -> Any:
        pass

    async def cleanup(self) -> None:
        pass


def test_base_agent_metadata():
    agent = MockAgent(agent_id="test-123", name="test-agent")
    
    # Test valid metadata
    agent.set_metadata("version", "1.0.0")
    assert agent.get_metadata("version") == "1.0.0"
    
    # Test invalid metadata keys (empty strings, whitespaces, non-string keys)
    with pytest.raises(ValueError, match="Metadata key must be a non-empty string"):
        agent.set_metadata("", "some-val")
        
    with pytest.raises(ValueError, match="Metadata key must be a non-empty string"):
        agent.set_metadata("   ", "some-val")

    with pytest.raises(TypeError, match="Metadata key must be a string"):
        agent.set_metadata(123, "some-val")
