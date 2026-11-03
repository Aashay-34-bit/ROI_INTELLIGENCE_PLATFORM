# Changelog

## Phase 11

- 11.1: Added explicit provider selection, registry filtering, and Ollama startup health checks. Requests configured for an unavailable Ollama provider now fail with a clear 503 instead of silently using the mock adapter.
- 11.2: Added deterministic mock failure modes, retry/escalation trace fields, and an isolated HTTP escalation demo.
- 11.3: Jev decisions now gate configured routing rules, including a no-model billing handler, with a safe fallback when Jev fails.
- 11.4: Node traces now separate requested precision from verified observed precision and explain unverified adapter reports.
- 11.5: Strict classification and extraction requests now require a ready local Ollama placement; unsupported strict tasks record capability escalation or return an explicit 503.
- 11.6: Harness runs now execute every task against three or more candidate prompt configs, compare scores and cost, and append best/history JSON results.
- 11.7: Added Provider Truth counts for providers, precision verification, and recent 503 errors, with visible unverified badges and estimate labels in the dashboard.
- 11.8: Documented local-only Ollama mode, executable demos, Provider Truth, and an opt-in real-provider smoke target.
