CREATE SCHEMA IF NOT EXISTS system;

ALTER TABLE public.tag SET SCHEMA system;
ALTER TABLE public.layer_tag SET SCHEMA system;
ALTER TABLE public.dict SET SCHEMA system;
ALTER TABLE public.attachment_qgis SET SCHEMA system;
ALTER TABLE public.layer_styles SET SCHEMA system;