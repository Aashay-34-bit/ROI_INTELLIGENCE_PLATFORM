import json

import pytest

from app.edge.harness_optimizer import HarnessOptimizer
from app.settings import get_settings


@pytest.mark.asyncio
async def test_optimizer_picks_concise_when_synthetic_scorer_rewards_it(
    tmp_config_dir, monkeypatch
):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_MIN_LATENCY_MS", "0")
    monkeypatch.setenv("MOCK_MAX_LATENCY_MS", "0")
    get_settings.cache_clear()
    optimizer = HarnessOptimizer(tmp_config_dir / "harness" / "best.json")
    tasks = [
        {"id": "synthetic", "category": "reasoning", "input": "Solve this", "expected": "concise"}
    ]
    result = await optimizer.optimize(
        tasks,
        base_config={"prompt_style": "baseline"},
        candidates=[
            {"config_id": "baseline", "prompt_style": "baseline"},
            {"config_id": "concise", "prompt_style": "concise"},
            {"config_id": "few-shot", "prompt_style": "few_shot"},
        ],
    )
    assert result.chosen_config["prompt_style"] == "concise"
    assert result.improvement_over_baseline > 0
    assert result.configs_evaluated == 3
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_optimizer_appends_history(tmp_config_dir, monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_MIN_LATENCY_MS", "0")
    monkeypatch.setenv("MOCK_MAX_LATENCY_MS", "0")
    get_settings.cache_clear()
    optimizer = HarnessOptimizer(tmp_config_dir / "harness" / "best.json")
    tasks = [{"id": "one", "category": "generation", "input": "Hello", "expected": "hello"}]
    await optimizer.optimize(tasks)
    await optimizer.optimize(tasks)
    rows = [json.loads(line) for line in optimizer.history_path.read_text().splitlines()]
    assert len(rows) == 2
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_optimizer_requires_two_candidates(tmp_config_dir, monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="at least two"):
        await HarnessOptimizer(tmp_config_dir / "harness" / "best.json").optimize(
            [], candidates=[{"prompt_style": "baseline"}]
        )
    get_settings.cache_clear()
