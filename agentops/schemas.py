"""Pydantic contracts for runs and evaluations."""
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class EvaluationResult(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    explanation: str

class TraceStep(BaseModel):
    index: int
    kind: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    started_at: datetime = Field(default_factory=utc_now)
    duration_ms: float = 0.0
    status: str = "ok"
    error: str | None = None

class RunRecord(BaseModel):
    id: str
    agent_name: str
    question: str
    final_output: Any = None
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: float = 0.0
    steps: list[TraceStep] = Field(default_factory=list)
    evaluations: list[EvaluationResult] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0

class DemoRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    expected_answer: str | None = None
    context: str = (
        "Our standard refund policy allows customers to request a refund "
        "within 30 days of purchase."
    )
    required_evidence: list[str] = Field(default_factory=lambda: ["30 days"])
    input_tokens: int = Field(default=250, ge=0)
    output_tokens: int = Field(default=60, ge=0)
