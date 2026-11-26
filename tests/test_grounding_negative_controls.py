"""Negative controls: answers that are known to be wrong must fail the grounding check.

If an evaluator cannot fail on these, a green pass rate says nothing about the agent.
"""
import pytest
from agentops.evaluators import grounding

CONTEXT = (
    "Our standard refund policy allows customers to request a refund "
    "within 30 days of purchase."
)
EVIDENCE = ["30 days"]


def test_correct_answer_passes():
    result = grounding("The refund window is 30 days.", CONTEXT, EVIDENCE)
    assert result.passed and result.applicable and result.name == "lexical_grounding"


def test_negated_claim_fails():
    assert not grounding("The refund window is not 30 days.", CONTEXT, EVIDENCE).passed


def test_contradiction_with_invented_number_fails():
    result = grounding("It is not 30 days. It's 90.", CONTEXT, EVIDENCE)
    assert not result.passed and "90" in result.explanation


def test_invented_number_next_to_true_fact_fails():
    result = grounding("Refunds are within 30 days, and shipping takes 5 days.", CONTEXT, EVIDENCE)
    assert not result.passed


def test_evidence_missing_from_context_fails():
    other_context = "Refunds are handled by support."
    assert not grounding("The refund window is 30 days.", other_context, EVIDENCE).passed


def test_empty_evidence_is_not_applicable_rather_than_a_pass():
    result = grounding("anything", CONTEXT, [])
    assert result.applicable is False


# Known lexical limits. strict xfail: if one starts passing, the test flags it for removal.
@pytest.mark.xfail(strict=True, reason="phrase attributed to wrong subject; needs semantic judge")
def test_wrong_subject_attribution_is_not_detected():
    assert not grounding("Competitors typically offer 30 days.", CONTEXT, EVIDENCE).passed


@pytest.mark.xfail(strict=True, reason="non-numeric invented claim; needs semantic judge")
def test_invented_non_numeric_claim_is_not_detected():
    answer = "Refunds are within 30 days, plus free lifetime shipping."
    assert not grounding(answer, CONTEXT, EVIDENCE).passed
