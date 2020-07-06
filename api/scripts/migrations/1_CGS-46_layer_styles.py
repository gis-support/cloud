def run_migration(app):

    sql = """
    ALTER TABLE system.layer_styles SET SCHEMA public;
    """

    app._db.execute_sql(sql)
