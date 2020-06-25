import importlib
from pathlib import Path

from app.create import create_app

from app.db.migrations.migration import Migration
from app.db.migrations.utils import get_scripts, insert_migrations
from app.db.tables import create_tables


def run_python_migration(app, script: Path):
    module_name = script.name.split(".")[0]
    module = importlib.import_module(f"scripts.migrations.{module_name}")
    module.run_migration(app)


def run_sql_migration(app, script: Path):
    sql = script.read_text()
    app._db.execute_sql(sql)


def main(app):
    query_executed_scripts = Migration.select(Migration.script).tuples()
    executed_scripts = [row[0] for row in query_executed_scripts]

    scripts = get_scripts()

    scripts_to_be_executed = [script for script in scripts if script.name not in executed_scripts]
    scripts_to_be_executed.sort(key=lambda x: Migration.script_sorter(x.name))

    if len(scripts_to_be_executed) == 0:
        return 0

    with app._db.atomic():

        create_tables(app._db)

        script: Path
        for script in scripts_to_be_executed:

            print(f"{script.name}...", end="")

            try:
                if script.name.endswith(".py"):
                    run_python_migration(app, script)
                elif script.name.endswith(".sql"):
                    run_sql_migration(app, script)
            except:
                print("")
                raise
            else:
                print("\t\tDONE")

        insert_migrations(scripts_to_be_executed)

    return 0


if __name__ == '__main__':
    app = create_app('development')
    main(app)
