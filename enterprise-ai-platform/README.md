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
- `GET /v1/metrics/provider_truth`
- `GET /v1/models`
- `POST /v1/eval/run?mode=benchmark|harness`

SQLite stores per-request metrics. Summary values include cost, estimated savings against the advanced-model baseline, retry/escalation rates, parallel efficiency, success rate, and critical-path latency. The dashboard has six tabs for metrics, category breakdown, parallelism, quantization, retries, and models.

## Develop

`make install`, `make test`, `make lint`, `make seed`, `make eval`, `make demo-escalate`, `make demo-jev-routing`, `make demo-harness`, `make test-real-ollama`, `make up`, and `make down` wrap common tasks. YAML defaults live in `config/`. Add a model entry to `models.yaml` and give it a provider adapter; add deterministic match rules to `rules.yaml`. Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OLLAMA_BASE_URL` to configure optional provider credentials/endpoints. Mock providers drive the local demo without credentials.

Harness runs are separate from request handling. They test prompt-style and memory-policy candidates and save the selected config under `config/harness/best.json`.

## Local-only mode

Install [Ollama](https://ollama.com/download), then pull the configured model and start the local service:

```powershell
ollama pull qwen3.5:4b
ollama serve
```

Set `MODEL_PROVIDER=ollama` and `OLLAMA_BASE_URL=http://localhost:11434` in `.env` (or the process environment), then start the API with `uv run uvicorn app.main:app --reload`. The model tag is `qwen3.5:4b`; no OpenAI or Anthropic key is needed in this mode. In another terminal, start the dashboard with `uv run streamlit run app/dashboard/app.py`, submit a classification request, and inspect the trace for `provider="ollama"` and `model_id="qwen3.5:4b"`. Run `make test-real-ollama` for an opt-in local smoke check. The default `make test` suite remains mock-only and makes no model network calls.

If requests return `503 ollama_unreachable`, check that `ollama list` includes `qwen3.5:4b` and that the service is listening at `OLLAMA_BASE_URL`. A 404 from `/api/tags` usually means the base URL is incorrect.

## Escalation demo

Run `make demo-escalate`. The command starts an isolated local API, forces the first small mock model call to fail, and prints a trace showing the retry and escalation to the medium model.

## Jev routing demo

Run `make demo-jev-routing`. A duplicate-charge request is classified as `refund_request=Yes` and routed to the billing rule handler without a model call.

## Harness optimizer

Run `make demo-harness` to score at least three prompt configurations against `config/eval_tasks.yaml`. Results and run history are written to `config/harness/best.json` and `config/harness/history.jsonl`. The current mock scorer is deterministic; its score is an evaluation result over the configured task set, not a claim about production quality.

## Provider Truth

The dashboard's **Provider Truth** page and `GET /v1/metrics/provider_truth` show provider/edge counts, verified and unverified precision counts, recent 503 errors, and recent node details. An `UNVERIFIED` badge means the adapter did not confirm the runtime precision. Savings and quantization deltas remain estimates until an evaluation run is available.

## Verification

- A1: The full default mock suite passes without external model calls (30 tests passed).
- A2: Opt-in only; run `make test-real-ollama` on a machine with Ollama and `qwen3.5:4b` installed. Ollama was not available in this development environment.
- A3: Verified by an HTTP smoke test: unavailable Ollama returned 503 with `error=ollama_unreachable`.
- A4: Mock and respx Ollama precision tests pass, including matching and mismatching observed precision values.
- A5: `scripts/demo_escalate.py` completed; trace showed two attempts and escalation from `mock-small-fp8` to `mock-medium-fp8`.
- A6: `scripts/demo_jev_routing.py` completed; Jev selected `refund_request=Yes`, billing handler returned the result, and trace had zero model nodes.
- A7: Strict edge placement, cloud capability escalation, and unavailable-edge 503 tests pass with respx-mocked Ollama.
- A8: `scripts/demo_harness.py` evaluated 3 configs over 11 tasks and persisted best/history JSON files.
- A9: Provider Truth aggregation and metrics tests pass; dashboard page added.
- A10: This section documents local Ollama setup and trace verification.
