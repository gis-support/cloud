REVOKE CREATE ON SCHEMA public FROM public;
CREATE TABLE IF NOT EXISTS public.layer_styles (
    id serial NOT NULL,
    f_table_catalog varchar NULL,
    f_table_schema varchar NULL,
    f_table_name varchar NULL,
    f_geometry_column varchar NULL,
    stylename text NULL,
    styleqml xml NULL,
    stylesld xml NULL,
    useasdefault bool NULL,
    description text NULL,
    "owner" varchar(63) NULL,
    ui xml NULL,
    update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT layer_styles_pkey PRIMARY KEY (id)
);