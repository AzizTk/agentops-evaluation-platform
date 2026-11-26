"""Transparent deterministic evaluators."""
import json
import re
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

_NEGATION = re.compile(
    r"\b(?:not|no|never|cannot|without|incorrect|wrong|false|untrue)\b|n't", re.IGNORECASE
)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def grounding(
    output: str, context: str, required_evidence: Sequence[str]
) -> EvaluationResult:
    """Lexical grounding baseline (not an entailment check).

    A required phrase counts as grounded only if it appears in the context AND in an
    output sentence that is not negated. Numbers in the output that never appear in the
    context fail the check as unsupported claims. An empty evidence list is reported as
    not applicable instead of an automatic pass, so it cannot inflate pass rates.

    Known limits: it cannot detect a true phrase attached to an invented non-numeric
    claim, or a phrase attributed to the wrong subject. Use a calibrated judge for that.
    """
    name = "lexical_grounding"
    if not required_evidence:
        return EvaluationResult(
            name=name,
            score=1.0,
            passed=True,
            applicable=False,
            explanation="No required evidence supplied; check not applicable.",
        )
    context_cf = context.casefold()
    sentences = [x for x in _SENTENCE_SPLIT.split(output) if x.strip()]
    problems: list[str] = []
    absent: set[str] = set()
    for phrase in required_evidence:
        phrase_cf = phrase.casefold()
        if phrase_cf not in context_cf:
            absent.add(phrase)
            problems.append(f"'{phrase}' not in context")
            continue
        asserting = [
            x for x in sentences if phrase_cf in x.casefold() and not _NEGATION.search(x)
        ]
        if not asserting:
            absent.add(phrase)
            problems.append(f"'{phrase}' not asserted in answer (missing or negated)")
    context_numbers = set(_NUMBER.findall(context))
    unsupported = sorted(set(_NUMBER.findall(output)) - context_numbers)
    if unsupported:
        problems.append(f"numbers not in context: {', '.join(unsupported)}")
    score = (len(required_evidence) - len(absent)) / len(required_evidence)
    if unsupported:
        score = min(score, 0.5)
    passed = not problems
    return EvaluationResult(
        name=name,
        score=score,
        passed=passed,
        explanation=(
            "Lexical check: required evidence is asserted in the answer and present in context."
            if passed
            else "Lexical check failed: " + "; ".join(problems)
        ),
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
