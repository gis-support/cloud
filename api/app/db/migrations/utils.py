from pathlib import Path
from typing import List, Optional

from app.db.migrations.migration import Migration
from app.default_config import Config

migrations_path = Path(Config.ROOT_DIRECTORY, "scripts", "migrations")

def get_scripts() -> List[Path]:
    result: List[Path] = []
    for path in migrations_path.iterdir():
        if path.name.endswith(".py"):
            result.append(path)

    return result


def insert_migrations(scripts: Optional[List[Path]] = None):
    scripts = scripts or get_scripts()

    if len(scripts) == 0:
        return

    rows = [{"script": script.name} for script in scripts]
    Migration.insert_many(rows).execute()
