"""Shared pytest fixtures."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def temp_output_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CSV exports to a temporary file."""
    output_file = tmp_path / "exports" / "scraped_data.csv"
    monkeypatch.setattr("app.config.settings.OUTPUT_FILE", str(output_file))
    return output_file


@pytest.fixture()
def temp_snapshot_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect snapshot storage to a temporary SQLite database."""
    database_file = tmp_path / "data" / "snapshots.db"
    monkeypatch.setattr("app.config.settings.SNAPSHOT_DB_FILE", str(database_file))
    return database_file


@pytest.fixture(autouse=True)
def disable_global_cache() -> Generator[None, None, None]:
    """Disable shared cache side effects between tests."""
    with patch("app.utils.decorators.cache_manager.get", new_callable=AsyncMock) as mock_get, patch(
        "app.utils.decorators.cache_manager.set", new_callable=AsyncMock
    ):
        mock_get.return_value = None
        yield
