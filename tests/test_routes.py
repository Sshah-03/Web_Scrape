"""Tests for FastAPI routes and CSV export."""

from pathlib import Path
import sqlite3
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.models.schemas import FakeStoreItem, HackerNewsItem, RedditItem, ScrapeResponse
from app.services.export_service import export_to_csv
from app.services.snapshot_service import init_snapshot_db


def test_scrape_endpoint_returns_partial_success(client: TestClient) -> None:
    """The scrape route should tolerate a single scraper failure."""
    mock_hn = AsyncMock()
    mock_hn.scrape.return_value = [HackerNewsItem(title="HN", url="https://example.com", score=1)]

    mock_rd = AsyncMock()
    mock_rd.scrape.side_effect = RuntimeError("reddit failed")

    mock_fs = AsyncMock()
    mock_fs.scrape.return_value = [FakeStoreItem(title="FS", price=1.0, category="tools")]

    with patch("app.api.routes.hn", mock_hn), patch("app.api.routes.rd", mock_rd), patch(
        "app.api.routes.fs", mock_fs
    ), patch("app.api.routes.export_to_csv") as mock_export:
        response = client.get("/scrape")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    mock_export.assert_called_once()


def test_export_endpoint_returns_csv(client: TestClient, tmp_path: Path) -> None:
    """The export route should stream the generated CSV file."""
    output_file = tmp_path / "scraped_data.csv"
    output_file.write_text("title,score\nTest,1\n", encoding="utf-8")

    with patch("app.api.routes.scrape_all", new_callable=AsyncMock) as mock_scrape, patch(
        "app.api.routes.export_to_csv", return_value=str(output_file)
    ) as mock_export:
        mock_scrape.return_value = ScrapeResponse(
            data=[RedditItem(title="Post", score=2, url="https://reddit.com/r/python/1")]
        )
        response = client.get("/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    mock_export.assert_called_once()


def test_export_service_writes_csv(temp_output_file: Path) -> None:
    """The export service should write a CSV file with pandas."""
    file_path = export_to_csv([{"title": "Story", "score": 10}])

    assert file_path == str(temp_output_file)
    assert temp_output_file.exists()
    assert "Story" in temp_output_file.read_text(encoding="utf-8")


def test_scrape_endpoint_ignores_csv_refresh_failure(client: TestClient) -> None:
    """The scrape route should still succeed if auto CSV refresh fails."""
    mock_hn = AsyncMock()
    mock_hn.scrape.return_value = [HackerNewsItem(title="HN", url="https://example.com", score=1)]

    mock_rd = AsyncMock()
    mock_rd.scrape.return_value = []

    mock_fs = AsyncMock()
    mock_fs.scrape.return_value = []

    with patch("app.api.routes.hn", mock_hn), patch("app.api.routes.rd", mock_rd), patch(
        "app.api.routes.fs", mock_fs
    ), patch("app.api.routes.export_to_csv", side_effect=RuntimeError("disk error")):
        response = client.get("/scrape")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_snapshot_endpoint_stores_data(client: TestClient, temp_snapshot_db: Path) -> None:
    """The snapshot route should persist the current results to SQLite."""
    init_snapshot_db()

    response = client.post(
        "/snapshots",
        json={
            "data": [
                {"title": "HN", "url": "https://example.com", "score": 10},
                {"title": "Product", "price": 11.5, "category": "tools"},
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Snapshot stored successfully"
    assert payload["item_count"] == 2

    with sqlite3.connect(temp_snapshot_db) as connection:
        stored_row = connection.execute(
            "SELECT item_count, payload FROM snapshots WHERE id = ?",
            (payload["snapshot_id"],),
        ).fetchone()

    assert stored_row is not None
    assert stored_row[0] == 2
    assert "Product" in stored_row[1]


def test_snapshot_endpoint_rejects_empty_payload(client: TestClient) -> None:
    """The snapshot route should require at least one item."""
    response = client.post("/snapshots", json={"data": []})

    assert response.status_code == 400
    assert response.json()["detail"] == "Snapshot data cannot be empty"


def test_snapshot_list_endpoint_returns_recent_snapshots(
    client: TestClient, temp_snapshot_db: Path
) -> None:
    """The snapshot list route should return stored snapshots."""
    init_snapshot_db()

    with sqlite3.connect(temp_snapshot_db) as connection:
        connection.execute(
            """
            INSERT INTO snapshots (created_at, item_count, payload)
            VALUES (?, ?, ?)
            """,
            ("2026-03-24T00:00:00+00:00", 3, '[{"title":"Story"}]'),
        )
        connection.commit()

    response = client.get("/snapshots")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["snapshots"]) == 1
    assert payload["snapshots"][0]["item_count"] == 3
