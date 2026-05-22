"""Agent Registry — Manages agent lifecycle and metadata."""

import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"
    TERMINATED = "terminated"


class AgentRegistry:
    def __init__(self, storage_backend: str = "memory"):
        self.storage_backend = storage_backend
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._index: Dict[str, List[str]] = {}

    def register(self, name: str, agent_type: str, config: Optional[Dict] = None) -> str:
        config = config or {}
        routing = config.get("routing", {}) or {}
        routes = config.get("routes") or routing.get("routes")
        traffic_split = config.get("traffic_split")
        
        def validate_policy(policy_data):
            if not policy_data:
                raise ValueError("Route policy cannot be empty")
                
            if isinstance(policy_data, dict):
                targets = list(policy_data.keys())
                if len(targets) != len(set(targets)):
                    raise ValueError("Duplicate route targets are not allowed")
                total_weight = 0
                for target, weight in policy_data.items():
                    if not isinstance(weight, (int, float)) or isinstance(weight, bool):
                        raise TypeError("Route weights must be numeric")
                    if weight <= 0:
                        raise ValueError("Route weights must be positive")
                    total_weight += weight
                if abs(total_weight - 100.0) > 1e-9:
                    raise ValueError("Route weights must total 100")
            elif isinstance(policy_data, list):
                targets = []
                total_weight = 0
                for item in policy_data:
                    if not isinstance(item, dict):
                        raise TypeError("Route items must be dicts")
                    target = item.get("target")
                    weight = item.get("weight")
                    if target is None or weight is None:
                        raise ValueError("Route item is missing target or weight")
                    targets.append(target)
                    if not isinstance(weight, (int, float)) or isinstance(weight, bool):
                        raise TypeError("Route weights must be numeric")
                    if weight <= 0:
                        raise ValueError("Route weights must be positive")
                    total_weight += weight
                if len(targets) != len(set(targets)):
                    raise ValueError("Duplicate route targets are not allowed")
                if abs(total_weight - 100.0) > 1e-9:
                    raise ValueError("Route weights must total 100")
            else:
                raise TypeError("Invalid route policy format")

        if routes is not None:
            validate_policy(routes)
        if traffic_split is not None:
            validate_policy(traffic_split)

        agent_id = str(uuid.uuid4())
        timestamp = time.time()
        self._agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "type": agent_type,
            "status": AgentStatus.PENDING.value,
            "config": config,
            "created_at": timestamp,
            "updated_at": timestamp,
            "version": "1.0.0",
            "metrics": {"tasks_completed": 0, "errors": 0, "uptime": 0},
        }
        group = agent_type.split(".")[0]
        if group not in self._index:
            self._index[group] = []
        self._index[group].append(agent_id)
        return agent_id

    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._agents.get(agent_id)

    def list(self, status: Optional[AgentStatus] = None, group: Optional[str] = None) -> List[Dict[str, Any]]:
        agents = self._agents.values()
        if status:
            agents = [a for a in agents if a["status"] == status.value]
        if group:
            agent_ids = self._index.get(group, [])
            agents = [a for a in agents if a["id"] in agent_ids]
        return list(agents)

    def update_status(self, agent_id: str, status: AgentStatus) -> bool:
        if agent_id not in self._agents:
            return False
        self._agents[agent_id]["status"] = status.value
        self._agents[agent_id]["updated_at"] = time.time()
        return True

    def delete(self, agent_id: str) -> bool:
        if agent_id not in self._agents:
            return False
        agent = self._agents.pop(agent_id)
        group = agent["type"].split(".")[0]
        if group in self._index and agent_id in self._index[group]:
            self._index[group].remove(agent_id)
        return True

    def count(self) -> int:
        return len(self._agents)
