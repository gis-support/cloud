def run_migration(app):

    sql = """
    GRANT SELECT ON TABLE public.layer_styles TO "admin";
    """

    app._db.execute_sql(sql)
