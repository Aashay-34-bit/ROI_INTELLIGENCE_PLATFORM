# Enterprise AI Intelligence & ROI Platform

Mock-first async FastAPI gateway, YAML model registry, pluggable routers, DAG execution, request metrics, ROI summaries, and Streamlit charts.

## Run it

Install Python 3.11+, `uv`, then run from this directory:

```powershell
Copy-Item .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

API auth uses `X-API-Key` (default `demo-key`). Submit a request:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/v1/request -Headers @{'X-API-Key'='demo-key'} -ContentType 'application/json' -Body '{"input":"Classify this message: great service","task_category":"classification"}'
```

For seeded activity, open another terminal and run `uv run python scripts/seed_demo_requests.py`. Launch the dashboard with `uv run streamlit run app/dashboard/app.py`. Docker users can run `docker compose up --build`.

## API

- `GET /health`
- `POST /v1/request` (include optional `metadata.subtasks` with nodes and `depends_on` to schedule a DAG)
- `GET /v1/request/{id}`
- `GET /v1/metrics/summary` and `/v1/metrics/timeseries`
- `GET /v1/models`
- `POST /v1/eval/run?mode=benchmark|harness`

SQLite stores per-request metrics. Summary values include cost, estimated savings against the advanced-model baseline, retry/escalation rates, parallel efficiency, success rate, and critical-path latency. The dashboard has six tabs for metrics, category breakdown, parallelism, quantization, retries, and models.

## Develop

`make install`, `make test`, `make lint`, `make seed`, `make eval`, `make up`, and `make down` wrap common tasks. YAML defaults live in `config/`. Add a model entry to `models.yaml` and give it a provider adapter; add deterministic match rules to `rules.yaml`. Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OLLAMA_BASE_URL` to configure optional provider credentials/endpoints. Mock providers drive the local demo without credentials.

Harness runs are separate from request handling. They test prompt-style and memory-policy candidates and save the selected config under `config/harness/best.json`.
