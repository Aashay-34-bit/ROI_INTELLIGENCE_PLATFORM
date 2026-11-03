import asyncio
import shutil
import sys

import pytest

from app.providers.mock_adapter import reset_flaky_state

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(autouse=True)
def reset_mock_mode(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "stable")
    reset_flaky_state()
    yield
    reset_flaky_state()


@pytest.fixture
def tmp_config_dir(tmp_path):
    source = __import__("pathlib").Path(__file__).resolve().parents[1] / "config"
    target = tmp_path / "config"
    shutil.copytree(source, target)
    return target
