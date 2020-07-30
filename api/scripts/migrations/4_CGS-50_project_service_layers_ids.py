def run_migration(app):
    app._db.execute_sql("ALTER TABLE system.project ADD COLUMN IF NOT EXISTS service_layers_ids jsonb not null default '[]'")
