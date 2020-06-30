import argparse
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


def main(app):
    Migration.create_table(safe=True)

    query_executed_scripts = Migration.select(Migration.script).tuples()
    executed_scripts = [row[0] for row in query_executed_scripts]

    scripts = get_scripts()

    scripts_to_be_executed = [script for script in scripts if script.name not in executed_scripts]
    scripts_to_be_executed.sort(key=lambda x: Migration.script_sorter(x.name))

    if len(scripts_to_be_executed) == 0:
        return 0

    with app._db.atomic():

        script: Path
        for script in scripts_to_be_executed:

            print(f"{script.name}... ", end="")

            try:
                if script.name.endswith(".py"):
                    run_python_migration(app, script)
            except:
                print("")
                raise
            else:
                print("\33[32m", "OK", '\33[0m')

        insert_migrations(scripts_to_be_executed)
        create_tables(app._db)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Uruchamia migracje bazy danych.'''
    )
    parser.add_argument(
        '-c', '--config', dest="config",
        help='Nazwa konfiguracji, dla której powinna zostać uruchomiona migracja.',
        choices=["production", "development"], default="development", type=str)

    args = parser.parse_args()
    config = args.config

    print(config.upper())
    app = create_app(config)
    main(app)

    print("")

    print("TESTING")
    app = create_app('testing')
    main(app)