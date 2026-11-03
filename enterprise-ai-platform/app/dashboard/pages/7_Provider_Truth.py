import os

import pandas as pd
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Provider Truth", layout="wide")
st.title("Provider Truth")

try:
    truth = requests.get(f"{API}/v1/metrics/provider_truth", timeout=5).json()
except requests.RequestException as error:
    st.error(f"Could not load provider metrics from {API}: {error}")
    st.stop()

if truth.get("has_real_calls"):
    st.success("Showing REAL calls in the last 100 requests.")
else:
    st.info("All MOCK — metrics are simulated.")

left, right = st.columns(2)
with left:
    st.subheader("Calls by provider / placement")
    st.dataframe(
        pd.DataFrame(
            [
                {"Provider": provider, "Count": count}
                for provider, count in truth["by_provider"].items()
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )
with right:
    st.subheader("Precision verification")
    st.dataframe(
        pd.DataFrame(
            [
                {"Verified": "True", "Count": truth["by_precision_verified"].get("true", 0)},
                {"Verified": "False", "Count": truth["by_precision_verified"].get("false", 0)},
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Last 5 provider errors (503)")
errors = truth.get("recent_errors", [])
if errors:
    st.dataframe(errors, hide_index=True, use_container_width=True)
else:
    st.caption("No provider 503 errors recorded.")

st.subheader("Recent request nodes")
nodes = truth.get("recent_nodes", [])
if nodes:
    rows = []
    for node in nodes:
        rows.append(
            {
                **node,
                "precision_badge": ("VERIFIED" if node.get("precision_verified") else "UNVERIFIED"),
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)
else:
    st.caption("No model nodes have been recorded yet.")

st.caption(
    "Estimated savings are a baseline estimate. Run `make demo-harness` for an evaluation comparison."
)
