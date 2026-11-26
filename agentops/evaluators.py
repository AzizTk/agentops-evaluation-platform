"""Transparent deterministic evaluators."""
import json
from collections.abc import Mapping, Sequence
from .schemas import EvaluationResult

def exact_match(actual: str, expected: str) -> EvaluationResult:
    passed = " ".join(actual.casefold().split()) == " ".join(expected.casefold().split())
    return EvaluationResult(name="exact_match", score=float(passed), passed=passed,
        explanation="Normalized output matches expected answer." if passed else "Normalized output differs from expected answer.")

def required_keys(actual: Mapping, keys: Sequence[str]) -> EvaluationResult:
    missing = [key for key in keys if key not in actual]
    score = 1.0 if not keys else (len(keys) - len(missing)) / len(keys)
    return EvaluationResult(name="required_keys", score=score, passed=not missing,
        explanation="All required keys are present." if not missing else f"Missing keys: {', '.join(missing)}")

def grounding(output: str, context: str, required_evidence: Sequence[str]) -> EvaluationResult:
    absent = [p for p in required_evidence if p.casefold() not in context.casefold() or p.casefold() not in output.casefold()]
    score = 1.0 if not required_evidence else (len(required_evidence) - len(absent)) / len(required_evidence)
    return EvaluationResult(name="grounding", score=score, passed=not absent,
        explanation="Required evidence appears in both context and answer." if not absent else f"Evidence not grounded: {', '.join(absent)}")

def task_completion(completed: bool) -> EvaluationResult:
    return EvaluationResult(name="task_completion", score=float(completed), passed=completed,
        explanation="Agent marked task complete." if completed else "Agent did not mark task complete.")

def parse_json_object(value: str) -> dict:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")
    return parsed
