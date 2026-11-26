# AgentOps — Agent Evaluation & Observability Platform

<p align="center"><strong>Evaluate. Trace. Compare. Improve.</strong><br/>A lightweight, self-hostable evaluation and observability layer for tool-using AI agents.</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi" />
<img src="https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest" />
<img src="https://img.shields.io/badge/License-MIT-green.svg" />
</p>

AgentOps measures agent reliability beyond whether a final answer looks plausible. It records execution traces, evaluates outputs against explicit criteria, tracks latency and tool usage, and exposes run history through an API.

## Why this exists
Agent workflows are multi-step systems. A fluent final response can still use the wrong tool, ignore evidence, return malformed data, or exceed a budget. AgentOps makes those failure modes inspectable and testable.

## Features
- Traceable runs: steps, tool calls, timestamps, errors, and final outputs.
- Deterministic evaluators: exact match, required keys, lexical evidence grounding (negation- and unsupported-number-aware), task completion.
- Operational metrics: duration, step count, token counts, tool calls, estimated cost.
- Human approval primitive for tools marked as sensitive.
- Persistent history: SQLite by default; PostgreSQL-compatible SQLAlchemy URL.
- FastAPI, Pydantic, pytest, Docker, and GitHub Actions.
- Provider-neutral runtime interface; included demo requires no API key.

## Architecture
```text
Client / Dashboard
       │ HTTP
       ▼
 FastAPI ─────── Runs API / Metrics
       │
       ▼
 Agent Runtime ── Tool Registry / Approval Gate
       │ events
       ▼
 Trace + Evaluators
       │
       ▼
 SQL Storage
```

## Quick start
Requires Python 3.11+.

```bash
git clone https://github.com/AzizTk/agentops-evaluation-platform.git
cd agentops-evaluation-platform
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentops.api:app --reload
```

Open http://127.0.0.1:8000/docs.

### Run the demo
```bash
curl -X POST http://127.0.0.1:8000/runs/demo \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the refund window?","expected_answer":"The refund window is 30 days."}'
```

Inspect history with `GET /runs`, one trace with `GET /runs/{run_id}`, and aggregate metrics with `GET /metrics/summary`.

## Evaluation model

| Evaluator | What it checks |
|---|---|
| Exact match | Normalized answer equals expected answer |
| Required keys | Structured output contains required fields |
| Lexical grounding | Required phrases are in the context and asserted (not negated) in the answer; numbers not in the context fail. Lexical baseline only; empty evidence is reported as not applicable |
| Task completion | Agent explicitly reports successful completion |

Scores are transparent regression signals, not claims of universal semantic understanding.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/runs/demo` | Execute included demo workflow |
| GET | `/runs` | List recent runs |
| GET | `/runs/{run_id}` | Retrieve trace and evaluations |
| GET | `/metrics/summary` | Aggregate reliability and runtime metrics |

### Optional dashboard

Install the dashboard extra and start the UI in a second terminal:

```bash
pip install -e ".[dashboard]"
streamlit run dashboard/app.py
```

The dashboard reads from the API at `http://127.0.0.1:8000`. Override this with `AGENTOPS_API_URL` if the API runs elsewhere.

## Human approval
Tools may be registered with `requires_approval=True`. The runtime blocks execution until approval is passed explicitly. This is a policy primitive; production use should add authenticated approval endpoints, identity, authorization, and durable audit controls.

## Configuration
Copy `.env.example` and configure:
- `AGENTOPS_DATABASE_URL` (default: `sqlite:///./agentops.db`)
- `AGENTOPS_COST_PER_1K_INPUT_TOKENS`
- `AGENTOPS_COST_PER_1K_OUTPUT_TOKENS`

Cost is an estimate based on caller-supplied token counts and configured rates, not provider billing data.

## Tests and Docker
```bash
pytest
docker compose up --build
```

## Project scope
The demo agent uses deterministic local logic so tracing, evaluation, persistence, and API paths work without credentials. It makes no external LLM calls by default. This is an engineering starter platform, not a hosted production service.

## Roadmap
- Provider adapters with structured usage extraction
- Background execution and distributed tracing
- Authentication, roles, and approval inbox
- Calibrated semantic judge evaluators
- OpenTelemetry export

## Author
**Aziz Taktak** · AI Engineer | Applied AI · Machine Learning · MLOps  
Portfolio: https://aziz-portfolio-deploy.vercel.app  
GitHub: https://github.com/AzizTk

## License
MIT — see [LICENSE](LICENSE).
