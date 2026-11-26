"""Transparent deterministic evaluators."""
import json
from collections.abc import Mapping, Sequence
from .schemas import EvaluationResult

def exact_match(actual: str, expected: str) -> EvaluationResult:
    passed = " ".join(actual.casefold().split()) == " ".join(
        expected.casefold().split()
    )
    explanation = (
        "Normalized output matches expected answer."
        if passed
        else "Normalized output differs from expected answer."
    )
    return EvaluationResult(
        name="exact_match",
        score=float(passed),
        passed=passed,
        explanation=explanation,
    )

def required_keys(actual: Mapping, keys: Sequence[str]) -> EvaluationResult:
    missing = [key for key in keys if key not in actual]
    score = 1.0 if not keys else (len(keys) - len(missing)) / len(keys)
    explanation = (
        "All required keys are present."
        if not missing
        else f"Missing keys: {', '.join(missing)}"
    )
    return EvaluationResult(
        name="required_keys",
        score=score,
        passed=not missing,
        explanation=explanation,
    )

def grounding(
    output: str, context: str, required_evidence: Sequence[str]
) -> EvaluationResult:
    absent = [
        phrase
        for phrase in required_evidence
        if phrase.casefold() not in context.casefold()
        or phrase.casefold() not in output.casefold()
    ]
    score = (
        1.0
        if not required_evidence
        else (len(required_evidence) - len(absent)) / len(required_evidence)
    )
    explanation = (
        "Required evidence appears in both context and answer."
        if not absent
        else f"Evidence not grounded: {', '.join(absent)}"
    )
    return EvaluationResult(
        name="grounding",
        score=score,
        passed=not absent,
        explanation=explanation,
    )

def task_completion(completed: bool) -> EvaluationResult:
    explanation = (
        "Agent marked task complete."
        if completed
        else "Agent did not mark task complete."
    )
    return EvaluationResult(
        name="task_completion",
        score=float(completed),
        passed=completed,
        explanation=explanation,
    )

def parse_json_object(value: str) -> dict:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")
    return parsed
