#!/usr/bin/env python3
"""Initialize PostgreSQL tables from SQLAlchemy ORM models in app/models/."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings  # noqa: E402
from app.db.schema import init_schema  # noqa: E402


def main() -> None:
    settings = Settings()
    init_schema(settings.database_url)
    target = settings.database_url.rsplit("@", 1)[-1]
    print(f"Initialized schema from app.models on {target}")


if __name__ == "__main__":
    main()
