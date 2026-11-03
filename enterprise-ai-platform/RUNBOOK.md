# Runbook

Commands below run from `enterprise-ai-platform/`.

1. Install Python 3.11 or newer, `uv`, then run `make install`.
2. Copy `.env.example` to `.env`; set a private `API_KEY` for non-demo use.
3. Run `make test` and `make lint`.
4. Start the API with `make dev`.
5. In another terminal, run `make seed` to submit 20 requests.
6. Visit `http://localhost:8000/docs` for the API and `http://localhost:8000/v1/metrics/summary` for ROI metrics.
7. Run `streamlit run app/dashboard/app.py` and open `http://localhost:8501` for the dashboard.
8. Run `make eval` for the configured benchmark or `curl -X POST 'http://localhost:8000/v1/eval/run?mode=harness'` to optimize and persist a harness config.
9. `make up` starts API and dashboard with Docker Compose; `make down` stops them.

The summary endpoint reports request counts, cost, estimated savings against an advanced-model baseline, success rate, retry/escalation rate, average parallel efficiency, and critical-path latency. `/v1/metrics/timeseries` returns hourly request and cost rollups. `/v1/models` lists registered models and capabilities.

API requests require the `X-API-Key` header. The default demo key is `demo-key`; replace it before exposing the service. SQLite persists metrics to `platform.db` in the working directory.
