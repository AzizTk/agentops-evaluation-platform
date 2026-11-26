"""FastAPI endpoints for agent runs, traces, and metrics."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from .schemas import DemoRunRequest, RunRecord
from .runtime import execute_demo
from .storage import init_db, save_run, get_run, list_runs

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(title="AgentOps Evaluation Platform",
    description="Trace, evaluate, and inspect tool-using AI agent runs.",
    version="0.1.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "agentops"}

@app.post("/runs/demo", response_model=RunRecord, status_code=201)
def create_demo_run(request: DemoRunRequest):
    run = execute_demo(request)
    save_run(run)
    return run

@app.get("/runs", response_model=list[RunRecord])
def get_runs(limit: int = Query(default=50, ge=1, le=200)):
    return list_runs(limit)

@app.get("/runs/{run_id}", response_model=RunRecord)
def get_run_detail(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.get("/metrics/summary")
def metrics_summary():
    runs = list_runs(200)
    evaluations = [e for run in runs for e in run.evaluations]
    total, count = len(runs), len(evaluations)
    return {
        "total_runs": total,
        "completed_runs": sum(r.status == "completed" for r in runs),
        "average_duration_ms": round(sum(r.duration_ms for r in runs) / total, 3) if total else 0,
        "average_evaluation_score": round(sum(e.score for e in evaluations) / count, 3) if count else None,
        "evaluation_pass_rate": round(sum(e.passed for e in evaluations) / count, 3) if count else None,
        "estimated_cost_total": round(sum(r.estimated_cost for r in runs), 8),
    }
