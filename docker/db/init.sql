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
    stylejson jsonb NULL,
    useasdefault bool NULL,
    description text NULL,
    "owner" varchar(63) NULL,
    ui xml NULL,
    update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT layer_styles_pkey PRIMARY KEY (id)
);
create or replace function tilebbox (z int, x int, y int, srid int = 3857)
    returns geometry
    language plpgsql immutable as
$func$
declare
    max numeric := 20037508.34;
    res numeric := (max*2)/(2^z);
    bbox geometry;
begin
    bbox := ST_MakeEnvelope(
        -max + (x * res),
        max - (y * res),
        -max + (x * res) + res,
        max - (y * res) - res,
        3857
    );
    if srid = 3857 then
        return bbox;
    else
        return ST_Transform(bbox, srid);
    end if;
end;
$func$;