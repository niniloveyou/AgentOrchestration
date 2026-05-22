import pytest
from src.sdk.client import OrchestratorClient

def test_sdk_client_blank_name_validation():
    client = OrchestratorClient(base_url="https://example.test", api_key="test")
    
    with pytest.raises(ValueError, match="Agent name cannot be empty or whitespace-only"):
        client.register_agent("   ", "worker.processor")
        
    with pytest.raises(ValueError, match="Agent name cannot be empty or whitespace-only"):
        client.register_agent("", "worker.processor")

    with pytest.raises(TypeError, match="Agent name must be a string"):
        client.register_agent(12345, "worker.processor")
