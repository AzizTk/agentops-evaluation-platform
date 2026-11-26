import pytest
from agentops.evaluators import exact_match, required_keys, grounding, parse_json_object

def test_exact_match_normalizes_case_and_whitespace():
    assert exact_match(" HELLO   world ", "hello world").passed

def test_exact_match_detects_mismatch():
    result = exact_match("30 days", "14 days")
    assert not result.passed and result.score == 0

def test_required_keys_reports_missing_keys():
    result = required_keys({"name": "Ada"}, ["name", "email"])
    assert result.score == 0.5 and "email" in result.explanation

def test_grounding_checks_context_and_answer():
    assert grounding("Refunds: 30 days", "Policy: 30 days", ["30 days"]).passed
    assert not grounding("Refunds: 14 days", "Policy: 30 days", ["30 days"]).passed

def test_json_object_rejects_array():
    with pytest.raises(ValueError):
        parse_json_object('["not", "object"]')
