# Evaluation design

AgentOps intentionally starts with transparent, deterministic checks. They are cheap to run in CI and useful for detecting regressions in agent behavior.

## Evaluator contract

Every evaluator returns:
- `name`: stable identifier for dashboards and comparisons
- `score`: numeric score in [0, 1]
- `passed`: threshold decision for this evaluator
- `explanation`: human-readable diagnostic

## Included checks

### Exact match
Case-folds and collapses whitespace before comparing output and expected answer. Suitable for fixed-format tasks, not open-ended generation.

### Required keys
Checks presence of required keys in a mapping. It does not validate field types or semantic correctness; combine it with a Pydantic schema for strict structured output.

### Lexical grounding (`lexical_grounding`)
Verifies each required evidence phrase appears in both the supplied context and answer. The phrase must appear in a non-negated answer sentence, and numbers in the answer that are absent from the context fail the check. An empty evidence list is `applicable=false` and is excluded from aggregate metrics. This is still a deliberately simple lexical baseline. It does not prove entailment or detect all hallucinations.

### Task completion
Records whether the runtime marked the task as completed. In a production agent, this should be tied to verified workflow outcomes rather than the model's self-report.

## Operational metrics

Run records retain wall-clock duration, trace steps, caller-provided token counts, and a configurable cost estimate. Token counts and pricing are caller inputs in this demo. They are not inferred from provider responses and should not be presented as authoritative billing.

## Production extensions

1. Add provider adapters that extract usage and request identifiers from actual responses.
2. Add evaluator versioning and immutable benchmark datasets.
3. Add semantic judges only with calibration sets, agreement analysis, and human review.
4. Add tenant isolation, authentication, access controls, and audit retention before exposing the service publicly.
5. Add OpenTelemetry spans for cross-service correlation.

## Negative controls

`tests/test_grounding_negative_controls.py` holds known-bad answers that must fail. Cases the lexical check cannot catch (wrong-subject attribution, invented non-numeric claims) are strict `xfail`s that document the limit and flag themselves when fixed.
