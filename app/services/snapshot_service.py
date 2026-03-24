"""Database service for persisting scraped-data snapshots."""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def _database_path() -> Path:
    """Resolve the snapshot database path relative to the project root."""
    configured_path = Path(settings.SNAPSHOT_DB_FILE)
    if configured_path.is_absolute():
        return configured_path

    project_root = Path(__file__).resolve().parents[2]
    canonical_path = project_root / configured_path
    legacy_path = Path.cwd() / configured_path

    # Prefer the canonical project-local database, but keep using the legacy
    # location if that file already exists and the canonical one does not.
    if legacy_path.exists() and not canonical_path.exists():
        return legacy_path

    return canonical_path


def init_snapshot_db() -> None:
    """Create the snapshots table if it does not already exist."""
    database_path = _database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                item_count INTEGER NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        connection.commit()

    logger.info("Snapshot database ready at %s", database_path)


def save_snapshot(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Persist a full snapshot of the current scraped dataset."""
    created_at = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(data)
    database_path = _database_path()

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO snapshots (created_at, item_count, payload)
            VALUES (?, ?, ?)
            """,
            (created_at, len(data), payload),
        )
        connection.commit()

    snapshot_id = cursor.lastrowid
    logger.info("Saved snapshot %s with %d items", snapshot_id, len(data))
    return {
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "item_count": len(data),
    }


def list_snapshots(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent snapshot metadata for display."""
    database_path = _database_path()
    if not database_path.exists():
        return []

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, item_count
            FROM snapshots
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "snapshot_id": row[0],
            "created_at": row[1],
            "item_count": row[2],
        }
        for row in rows
    ]
