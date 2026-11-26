"""Environment-based configuration."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("AGENTOPS_DATABASE_URL", "sqlite:///./agentops.db")
    input_cost_per_1k: float = float(os.getenv("AGENTOPS_COST_PER_1K_INPUT_TOKENS", "0.0005"))
    output_cost_per_1k: float = float(os.getenv("AGENTOPS_COST_PER_1K_OUTPUT_TOKENS", "0.0015"))

settings = Settings()
