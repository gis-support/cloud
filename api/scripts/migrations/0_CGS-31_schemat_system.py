def run_migration(app):

    sql = """
    CREATE SCHEMA IF NOT EXISTS system;
    
    ALTER TABLE IF EXISTS public.tag SET SCHEMA system;
    ALTER TABLE IF EXISTS public.layer_tag SET SCHEMA system;
    ALTER TABLE IF EXISTS public.dict SET SCHEMA system;
    ALTER TABLE IF EXISTS public.attachment_qgis SET SCHEMA system;
    """

    app._db.execute_sql(sql)
