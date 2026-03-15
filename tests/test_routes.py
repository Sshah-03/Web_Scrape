import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ScrapeResponse


class TestRoutes:
    """Test cases for API routes."""

    def test_scrape_all_endpoint(self):
        """Test the /scrape endpoint."""
        client = TestClient(app)

        # Mock the scrapers
        mock_hn = AsyncMock()
        mock_hn.scrape.return_value = []

        mock_rd = AsyncMock()
        mock_rd.scrape.return_value = []

        mock_fs = AsyncMock()
        mock_fs.scrape.return_value = []

        with patch('app.api.routes.hn', mock_hn), \
             patch('app.api.routes.rd', mock_rd), \
             patch('app.api.routes.fs', mock_fs):

            response = client.get("/scrape")

            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            # Verify scrapers were called concurrently (via asyncio.gather)
            mock_hn.scrape.assert_called_once()
            mock_rd.scrape.assert_called_once()
            mock_fs.scrape.assert_called_once()

    def test_export_csv_endpoint(self, tmp_path):
        """Test the /export endpoint."""
        client = TestClient(app)

        # Mock the scrape function and export service
        with patch('app.api.routes.scrape_all', new_callable=AsyncMock) as mock_scrape, \
             patch('app.api.routes.export_to_csv') as mock_export:

            mock_scrape.return_value = ScrapeResponse(data=[])

            output_file = tmp_path / "test_output.csv"
            output_file.write_text("a,b,c\n1,2,3\n")
            mock_export.return_value = str(output_file)

            response = client.get("/export")

            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/csv")
            mock_export.assert_called_once()