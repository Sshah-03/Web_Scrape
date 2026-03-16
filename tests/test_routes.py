"""Tests for FastAPI routes and CSV export."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.models.schemas import FakeStoreItem, HackerNewsItem, RedditItem, ScrapeResponse
from app.services.export_service import export_to_csv


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
    ):
        response = client.get("/scrape")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


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
