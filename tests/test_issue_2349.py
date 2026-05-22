import pytest
from src.agent.registry import AgentRegistry

def test_registry_route_weight_validation():
    registry = AgentRegistry()
    
    agent_id = registry.register("agent-1", "worker.processor", {
        "traffic_split": {"target-A": 40, "target-B": 60}
    })
    assert agent_id is not None
    
    with pytest.raises(ValueError, match="Route weights must total 100"):
        registry.register("agent-2", "worker.processor", {
            "traffic_split": {"target-A": 40, "target-B": 50}
        })
        
    with pytest.raises(ValueError, match="Route weights must total 100"):
        registry.register("agent-3", "worker.processor", {
            "routes": [
                {"target": "A", "weight": 70},
                {"target": "B", "weight": 20}
            ]
        })

    with pytest.raises(TypeError, match="Route weights must be numeric"):
        registry.register("agent-4", "worker.processor", {
            "traffic_split": {"target-A": "40", "target-B": 60}
        })
