import pytest
from agentops.runtime import Tool, ToolRegistry, ApprovalRequired, execute_demo
from agentops.schemas import DemoRunRequest

def test_demo_run_has_trace_and_evaluations():
    run = execute_demo(DemoRunRequest(question="When can I get a refund?",
        expected_answer="The refund window is 30 days."))
    assert run.status == "completed" and len(run.steps) == 2
    assert all(result.passed for result in run.evaluations)

def test_protected_tool_requires_approval():
    registry = ToolRegistry()
    registry.register(Tool("send_email", lambda recipient: recipient, requires_approval=True))
    with pytest.raises(ApprovalRequired):
        registry.execute("send_email", {"recipient": "person@example.com"})
    assert registry.execute("send_email", {"recipient": "person@example.com"}, approved=True) == "person@example.com"

def test_duplicate_tools_are_rejected():
    registry = ToolRegistry()
    registry.register(Tool("lookup", lambda: "a"))
    with pytest.raises(ValueError):
        registry.register(Tool("lookup", lambda: "b"))
