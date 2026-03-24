"""CSV export service."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)


def _output_path() -> Path:
    """Resolve the CSV output path relative to the project root."""
    configured_path = Path(settings.OUTPUT_FILE)
    if configured_path.is_absolute():
        return configured_path

    project_root = Path(__file__).resolve().parents[2]
    return project_root / configured_path


def export_to_csv(data: list[dict[str, Any]]) -> str:
    """Export normalized scraper output to CSV."""
    output_path = _output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(data).to_csv(output_path, index=False)
    logger.info("CSV exported to %s", output_path)
    return str(output_path)
