"""Agent runtime, trace capture, and approval-aware tool registry."""
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable
from uuid import uuid4
from .config import settings
from .schemas import DemoRunRequest, RunRecord, TraceStep
from .evaluators import exact_match, grounding, task_completion

@dataclass
class Tool:
    name: str
    function: Callable[..., Any]
    requires_approval: bool = False

class ApprovalRequired(RuntimeError):
    """Raised when a protected tool is invoked without approval."""

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def execute(self, name: str, payload: dict, approved: bool = False) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        tool = self._tools[name]
        if tool.requires_approval and not approved:
            raise ApprovalRequired(f"Approval required for tool '{name}'.")
        return tool.function(**payload)

class DemoAgent:
    """Deterministic retrieval-style demo; no external model/API is called."""
    name = "policy-assistant"

    def run(self, request: DemoRunRequest) -> tuple[str, list[TraceStep]]:
        t0 = perf_counter()
        retrieval = TraceStep(
            index=0,
            kind="retrieval",
            name="lookup_policy",
            input={"query": request.question},
            output={"context": request.context},
        )
        answer = (
            "The refund window is 30 days."
            if "30 days" in request.context
            else "The context does not specify a refund window."
        )
        generation = TraceStep(
            index=1,
            kind="generation",
            name="compose_answer",
            input={"context_length": len(request.context)},
            output=answer,
            duration_ms=(perf_counter() - t0) * 1000,
        )
        return answer, [retrieval, generation]

def execute_demo(request: DemoRunRequest) -> RunRecord:
    started = datetime.now(timezone.utc)
    timer = perf_counter()
    answer, steps = DemoAgent().run(request)
    completed = datetime.now(timezone.utc)
    duration = (perf_counter() - timer) * 1000
    evaluations = []
    if request.expected_answer is not None:
        evaluations.append(exact_match(answer, request.expected_answer))
    evaluations.extend(
        [
            grounding(answer, request.context, request.required_evidence),
            task_completion(True),
        ]
    )
    cost = (
        request.input_tokens / 1000 * settings.input_cost_per_1k
        + request.output_tokens / 1000 * settings.output_cost_per_1k
    )
    return RunRecord(
        id=str(uuid4()),
        agent_name=DemoAgent.name,
        question=request.question,
        final_output=answer,
        status="completed",
        started_at=started,
        completed_at=completed,
        duration_ms=duration,
        steps=steps,
        evaluations=evaluations,
        input_tokens=request.input_tokens,
        output_tokens=request.output_tokens,
        estimated_cost=cost,
    )
