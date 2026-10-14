import os
from dataclasses import dataclass

@dataclass
class AgentConfig:
    agent_name: str = "titan-liveops-incident-agent"
    model_name: str = "gemini-3.7-flash"
    project_id: str = os.getenv("GCP_PROJECT", "epic-liveops-prod")
    location: str = os.getenv("GCP_REGION", "us-central1")
    bigquery_dataset: str = "epic_liveops"
    use_local_mock: bool = os.getenv("USE_LOCAL_MOCK", "true").lower() == "true"
    temperature: float = 0.1

config = AgentConfig()
