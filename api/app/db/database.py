from playhouse.postgres_ext import PostgresqlExtDatabase

database = PostgresqlExtDatabase(
    None,
    register_hstore=False,
    autorollback=True,
    field_types={'geometry': 'geometry'}
)