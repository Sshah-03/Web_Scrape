
import logging


def setup_logging() -> None:
    """Set up basic logging configuration for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
