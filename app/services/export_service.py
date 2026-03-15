
import pandas as pd
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


def export_to_csv(data: List[Dict[str, Any]]) -> str:
    """Export data to CSV file.

    Args:
        data: List of dictionaries to export.

    Returns:
        Path to the exported CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(settings.OUTPUT_FILE, index=False)
    logger.info("CSV exported to %s", settings.OUTPUT_FILE)
    return settings.OUTPUT_FILE
