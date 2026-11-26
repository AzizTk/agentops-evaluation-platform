"""Optional Streamlit dashboard for browsing AgentOps run history."""
import os
import requests
import streamlit as st

API_URL = os.getenv("AGENTOPS_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AgentOps | Run Explorer", page_icon="🧭", layout="wide")
st.title("🧭 AgentOps Run Explorer")
st.caption("A lightweight view over evaluation traces and runtime metrics.")

@st.cache_data(ttl=10)
def fetch_json(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=5)
    response.raise_for_status()
    return response.json()

try:
    metrics = fetch_json("/metrics/summary")
    runs = fetch_json("/runs?limit=100")
except requests.RequestException as exc:
    st.error(f"Cannot reach the AgentOps API at {API_URL}: {exc}")
    st.info("Start the API with: uvicorn agentops.api:app --reload")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Total runs", metrics["total_runs"])
b.metric("Completed", metrics["completed_runs"])
c.metric("Avg. evaluation", metrics["average_evaluation_score"] if metrics["average_evaluation_score"] is not None else "—")
d.metric("Pass rate", metrics["evaluation_pass_rate"] if metrics["evaluation_pass_rate"] is not None else "—")

st.subheader("Recent runs")
if not runs:
    st.info("No runs yet. Submit a demo run through the API docs to populate this view.")
else:
    rows = [{
        "Run ID": run["id"][:8],
        "Agent": run["agent_name"],
        "Status": run["status"],
        "Duration (ms)": round(run["duration_ms"], 2),
        "Cost estimate": run["estimated_cost"],
        "Evaluations passed": sum(i["passed"] for i in run["evaluations"] if i.get("applicable", True)),
        "Evaluations total": sum(1 for i in run["evaluations"] if i.get("applicable", True)),
    } for run in runs]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    selected = st.selectbox("Inspect a run", options=[r["id"] for r in runs],
                            format_func=lambda value: next(r["question"][:65] for r in runs if r["id"] == value))
    detail = requests.get(f"{API_URL}/runs/{selected}", timeout=5)
    detail.raise_for_status()
    run = detail.json()
    left, right = st.columns(2)
    with left:
        st.markdown("**Question**")
        st.write(run["question"])
        st.markdown("**Final output**")
        st.write(run["final_output"])
    with right:
        st.markdown("**Evaluation results**")
        for item in run["evaluations"]:
            st.write(f"{'✅' if item['passed'] else '❌'} **{item['name']}** — {item['score']:.2f}")
            st.caption(item["explanation"])
    st.markdown("**Execution trace**")
    st.json(run["steps"])
