import os

import plotly.express as px
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Enterprise AI ROI", layout="wide")
st.title("Enterprise AI Intelligence & ROI")
try:
    data = requests.get(f"{API}/v1/metrics/summary", timeout=3).json()
except requests.RequestException:
    data = {
        "request_count": 0,
        "cost_usd": 0,
        "savings_pct": 0,
        "by_category": {},
        "parallel_efficiency": 0,
        "retry_rate": 0,
        "escalation_rate": 0,
    }
pages = st.tabs(
    ["Live metrics", "Routing breakdown", "Parallelism", "Quantization", "Retries", "Models"]
)
with pages[0]:
    a, b, c = st.columns(3)
    a.metric("Requests", data.get("request_count", 0))
    b.metric("Cost USD", f"{data.get('cost_usd', 0):.4f}")
    c.metric("Savings (ESTIMATE)", f"{data.get('savings_pct', 0):.1f}%")
    st.caption("ESTIMATE — run `make demo-harness` for a candidate comparison.")
with pages[1]:
    st.plotly_chart(
        px.pie(
            names=list(data.get("by_category", {})),
            values=list(data.get("by_category", {}).values()),
            title="Requests by task",
        ),
        use_container_width=True,
    )
with pages[2]:
    st.metric("Parallel efficiency", data.get("parallel_efficiency", 0))
    st.metric("Critical path latency ms", data.get("critical_path_latency_ms", 0))
with pages[3]:
    st.write("ESTIMATE — run `make demo-harness` first to compare evaluation candidates.")
with pages[4]:
    st.metric("Retry rate", data.get("retry_rate", 0))
    st.metric("Escalation rate", data.get("escalation_rate", 0))
with pages[5]:
    try:
        st.json(requests.get(f"{API}/v1/models", timeout=3).json())
    except requests.RequestException:
        st.info("API is unavailable")
