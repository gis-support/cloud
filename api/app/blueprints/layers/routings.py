#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid

import jwt
import psycopg2

from flask import Blueprint, jsonify, request, current_app, make_response, Response, send_file
from flasgger import swag_from

from app.blueprints.layers.dicts.dict import Dict
from app.blueprints.layers.layers_attachments import LayerAttachmentsManager
from app.blueprints.layers.tags.models import LayerTag
from app.blueprints.layers.utils import MAX_LAYER_NAME_LENGTH
from app.blueprints.projects.models import Project
from app.db.database import database
from app.docs import path_by
from app.db.general import token_required, layer_decorator
from app.helpers.cloud import Cloud, cloud_decorator
from app.helpers.layer import Layer
from shapely.geometry import shape
from psycopg2.sql import SQL, Identifier, Placeholder
from osgeo import osr
from osgeo import ogr
# Layer id sync
from app.blueprints.rdos.attachments.models import Attachment
from psycopg2.extensions import AsIs
import tempfile
import os.path as op
from os import environ
from io import BytesIO
import json

mod_layers = Blueprint("layers", __name__)
from app.blueprints.layers.tags import routings

GDAL_TO_PG = {
    "String": "character varying",
    "Integer": "integer",
    "Real": "real",
    "DateTime": "timestamp without time zone",
    "Date": "timestamp without time zone",
    "Integer64": "integer"
}


@mod_layers.route("/layers/max_name_length")
@swag_from(path_by(__file__, 'docs.layers.max_name_length.get.yml'))
@token_required
def layers_max_name_length():
    return jsonify({"data": MAX_LAYER_NAME_LENGTH})

@mod_layers.route('/layers', methods=['GET', 'POST'])
@swag_from(path_by(__file__, 'docs.layers.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs.layers.get.yml'), methods=['GET'])
@token_required
@cloud_decorator
def layers(cloud):
    if request.method == 'GET':
        return jsonify({"layers": cloud.get_layers()})
    elif request.method == 'POST':
        files = [request.files[f] for f in request.files]
        if not files:
            return jsonify({"error": "file is required"}), 401
        name = request.form.get("name")
        environ['SHAPE_ENCODING'] = request.form.get("encoding", 'cp1250')
        if not name:
            return jsonify({"error": "name is required"}), 401
        if cloud.layer_exists(name):
            return jsonify({"error": "layer already exists"}), 401

        if len(name) > MAX_LAYER_NAME_LENGTH:
            return jsonify({"error": f"character limit for table name exceeded ({MAX_LAYER_NAME_LENGTH})"}), 400

        temp_path = tempfile.mkdtemp()
        file_paths = []
        for f in files:
            file_path = op.join(temp_path, f.filename)
            f.save(file_path)
            file_paths.append(file_path)
        if len(file_paths) == 1:
            source = ogr.Open(file_paths[0], 0)
        else:
            for path in file_paths:
                try:
                    source = ogr.Open(path, 0)
                    if source:
                        break
                except:
                    continue
            else:
                return jsonify({"error": "file is invalid"}), 401
        layer = source.GetLayer()
        sref = layer.GetSpatialRef()
        epsg = None
        if sref:
            # Autodetect
            epsg = sref.GetAuthorityCode(None)
        if not epsg:
            # Get from request
            epsg = request.form.get("epsg", None)
        transform = None
        if epsg != "4326":
            if not epsg:
                return jsonify({"error": "epsg not recognized"}), 400
            inSpatialRef = osr.SpatialReference()
            inSpatialRef.ImportFromEPSG(int(epsg))
            inSpatialRef.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            outSpatialRef = osr.SpatialReference()
            outSpatialRef.ImportFromEPSG(4326)
            outSpatialRef.SetAxisMappingStrategy(
                osr.OAMS_TRADITIONAL_GIS_ORDER)
            transform = osr.CoordinateTransformation(
                inSpatialRef, outSpatialRef)
        ldefn = layer.GetLayerDefn()
        test_feature = layer.GetNextFeature()
        geom_type = test_feature.GetGeometryRef().GetGeometryName()
        layer.ResetReading()
        fields = [{
            "name": "geometry",
            "type": "geometry"  # Mixed content for shapefiles if geom_type set
        }]
        for n in range(ldefn.GetFieldCount()):
            fdefn = ldefn.GetFieldDefn(n)
            # RL-38 double id column
            if fdefn.name in set(map(lambda x: x['name'], fields)).union(set(['id'])):
                fdefn.name = f'_{fdefn.name}'
            fields.append({
                'name': fdefn.name,
                'type': GDAL_TO_PG[fdefn.GetTypeName()],
            })
        with current_app._db.atomic():
            cloud = Cloud({"app": current_app, "user": request.user})
            cloud.create_layer(name, fields, geom_type)
            with tempfile.SpooledTemporaryFile(mode='w') as tfile:
                columns = list(map(lambda f: f['name'], fields))
                count_features = 0
                for feature in layer:
                    the_geom = feature.GetGeometryRef()

                    if the_geom is None:
                        return jsonify({"error": "layer has at least one feature with empty geometry"}), 400

                    if transform:
                        the_geom.Transform(transform)

                    ewkt = f"SRID=4326;{the_geom.ExportToWkt()}"

                    feature_string = ''
                    if len(columns) == 1:
                        # W przypadku braku atrybutów
                        feature_string += ewkt + "\n"
                    else:
                        for idx, column in enumerate(columns):
                            # Pierwszy wiersz to geometria
                            if idx == 0:
                                feature_string += ewkt + "\t"
                            else:
                                field = feature.GetField(column)
                                if isinstance(field, str):
                                    field = " ".join(field.split())
                                if idx + 1 != len(columns):
                                    feature_string += f'{field}\t'
                                else:
                                    feature_string += f'{field}\n'
                    count_features += 1
                    try:
                        tfile.write(feature_string)
                    except UnicodeEncodeError:
                        tfile.write(feature_string.encode(
                            'utf8', 'replace').decode('utf8', 'replace'))
                tfile.seek(0)
                cur = current_app._db.cursor()
                cur.copy_from(tfile, '"{}"'.format(name), null='None', columns=list(
                    map(lambda c: '"{}"'.format(c), columns)))

            layer = Layer({"app": current_app, "user": request.user, "name": name})
            LayerAttachmentsManager.create_attachments_column(layer)

        return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 201


@mod_layers.route('/layers/<lid>', methods=['GET', 'DELETE'])
@swag_from(path_by(__file__, 'docs.layers.id.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.layers.id.delete.yml'), methods=['DELETE'])
@token_required
def layers_id(lid):
    if request.method == 'GET':
        """
        Get layer by ID with default permission
        Returns GeoJSON
        """
        @layer_decorator(permission="read")
        def get(layer, lid=None):
            return jsonify(layer.as_geojson())
        return get(lid=lid)

    elif request.method == 'DELETE':
        """
        Delete layer by ID only with owner permission
        Returns confirmation
        """
        @layer_decorator(permission="owner")
        def delete(layer, lid=None):
            layer.delete()
            return jsonify({"layers": "{} deleted".format(layer.name)})
        return delete(lid=lid)


@mod_layers.route('/layers/<lid>/style', methods=['GET', 'PUT'])
@swag_from(path_by(__file__, 'docs.style.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.style.put.yml'), methods=['PUT'])
@token_required
def layers_style(lid):
    if request.method == 'GET':
        """
        Get layer style
        Returns style
        """
        @layer_decorator(permission="read")
        def get(layer, lid=None):
            return jsonify({"style": layer.get_style()})
        return get(lid=lid)

    elif request.method == 'PUT':
        """
        Change layer style
        Returns confirmation
        """
        @layer_decorator(permission="owner")
        def post(layer, lid=None):
            data = request.get_json(force=True)
            try:
                style = layer.set_style(data)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            return jsonify({"style": style})
        return post(lid=lid)


@mod_layers.route('/layers/<lid>/settings', methods=['GET', 'DELETE', 'POST'])
@swag_from(path_by(__file__, 'docs.settings.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.settings.delete.yml'), methods=['DELETE'])
@swag_from(path_by(__file__, 'docs.settings.post.yml'), methods=['POST'])
@token_required
def layers_settings(lid):
    if request.method == 'GET':
        """
        Get layer settings by ID with owner permission
        Returns schema
        """
        @layer_decorator(permission="read")
        def get(layer, lid=None):
            return jsonify({"settings": layer.settings()})
        return get(lid=lid)

    elif request.method == 'DELETE':
        """
        Delete layer property by ID only with owner permission
        Returns confirmation
        """
        @layer_decorator(permission="owner")
        def delete(layer, lid=None):
            data = request.get_json(force=True)
            column_name = data.get('column_name')
            try:
                layer.remove_column(column_name)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            return jsonify({"settings": f"{column_name} deleted"})
        return delete(lid=lid)

    elif request.method == 'POST':
        """
        Add layer property by ID only with owner permission
        Returns confirmation
        """
        @layer_decorator(permission="owner")
        def post(layer, lid=None):
            data = request.get_json(force=True)
            column_name = data.get('column_name')
            column_type = data.get('column_type')
            layer_name = data.get('layer_name')
            if layer_name:
                try:
                    layer.change_name(layer_name, callbacks=[
                        Attachment.sync,
                        LayerTag.update_layer_id,
                        Dict.update_layer_id,
                        Project.update_active_layer_id,
                        Project.update_additional_layers_ids
                    ])

                    return jsonify({"settings": layer.lid})
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
            try:
                if column_type == "dict":
                    values = data.get("values", [])
                    layer.add_dict_column(column_name, values)
                else:
                    layer.add_column(column_name, column_type)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            return jsonify({"settings": f"{column_name} added"})
        return post(lid=lid)

@mod_layers.route('/layers/<lid>/settings/dicts/values')
@swag_from(path_by(__file__, 'docs.layers.lid.settings.dicts.values.get.yml'), methods=['GET'])
@token_required
def layers_lid_settings_dicts_get(lid: str):

    @layer_decorator(permission="read")
    def get(layer, lid=None):
        query = Dict.select().where(Dict.layer_id == layer.lid)
        result = []
        for row in query:
            row_dict = {
                "values": row.get_values(),
                "column_name": row.column_name
            }
            result.append(row_dict)

        return jsonify({"data": result})

    return get(lid=lid)


@mod_layers.route('/layers/<lid>/settings/dicts/<column_name>/values', methods=["GET", "PUT"])
@swag_from(path_by(__file__, 'docs.layers.lid.settings.dicts.column_name.values.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.layers.lid.settings.dicts.column_name.values.put.yml'), methods=['PUT'])
@token_required
def layers_lid_settings_dicts_column_name_get(lid: str, column_name: str):

    @layer_decorator(permission="read")
    def get(layer, lid=None):

        try:
            if not layer.column_exists(column_name):
                return jsonify({"error": f"column {column_name} does not exist"}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if (dict_ := Dict.get_or_none(layer_id=layer.lid, column_name=column_name)) is not None:
            values = dict_.get_values()
            return jsonify({"data": values})
        else:
            return jsonify({"error": f"column {column_name} is not a dictitionary column"}), 400

    @layer_decorator(permission="write")
    def put(layer, lid=None):
        try:
            if not layer.column_exists(column_name):
                return jsonify({"error": f"column {column_name} does not exist"}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if (dict_ := Dict.get_or_none(layer_id=layer.lid, column_name=column_name)) is not None:
            values = request.get_json(force=True)["data"]
            current_values = dict_.get_values()

            with current_app._db.atomic():
                dict_.set_values(values)

                style = layer.get_style()

                if style["renderer"] == "categorized":
                    removed_values = set(current_values) - set(values)

                    current_categories = style["categories"]
                    current_categories = [cat for cat in current_categories if cat["value"] not in removed_values]

                    style["categories"] = current_categories
                    layer.set_style(style)

            return jsonify({"data": style}), 200
        else:
            return jsonify({"error": f"column {column_name} is not a dictitionary column"}), 400

    if request.method == "GET":
        return get(lid=lid)
    if request.method == "PUT":
        return put(lid=lid)


@mod_layers.route('/layers/<lid>/categories/<attr>', methods=['GET'])
@swag_from(path_by(__file__, 'docs.categories.get.yml'), methods=['GET'])
@token_required
def layer_categories(lid, attr):
    """
    Get layer categories by ID with read permission
    Returns schema
    """
    @layer_decorator(permission="read")
    def get(layer, lid=None, attr=None):
        try:
            return jsonify({"categories": layer.categories(attr)})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return get(lid=lid, attr=attr)


@mod_layers.route('/mvt/<lid>/<int:z>/<int:x>/<int:y>', methods=['GET'])
@token_required
@layer_decorator(permission="read")
def lid(layer, lid, z=0, x=0, y=0):
    tile = create_mvt_tile(z, x, y, layer.name)
    if not tile:
        return ('', 204)
    response = make_response(tile)
    response.headers['Content-Type'] = "application/octet-stream"
    return response


def create_mvt_tile(z, x, y, name):
    cur = current_app._db.cursor()
    #TODO: hotfix
    '''
    SELECT ST_AsMVT(tile) FROM (SELECT UNNEST(SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name = %s AND column_name NOT IN ('geometry')),
        ST_AsMVTGeom(ST_Buffer(ST_transform(geometry, 3857), 0),tilebbox(%s, %s, %s, 3857),4096,256,true) AS geom FROM {}) AS tile
    '''
    query = '''
        SELECT column_name from information_schema.columns WHERE table_name = %s
    '''
    cur.execute(query, (name,))
    columns = [f'"{row[0]}"' for row in cur.fetchall() if row[0] not in [
        'geometry']]
    query = SQL('''
        SELECT ST_AsMVT(tile) FROM (SELECT %s,
        ST_AsMVTGeom(ST_transform(geometry, 3857),tilebbox(%s, %s, %s, 3857),4096,50,true) AS geom FROM {}) AS tile
    ''').format(Identifier(name))
    cur.execute(query, (AsIs(",".join(columns)), z, x, y))
    tile = cur.fetchone()[0]
    return tile.tobytes()


@mod_layers.route('/layers/<lid>/export/geojson', methods=['POST'])
@swag_from(path_by(__file__, 'docs.export.geojson.post.yml'), methods=['POST'])
@token_required
def layers_export_geojson(lid):
    if request.method == 'POST':
        """
        Export layer to file
        Returns GeoJSON
        """
        @layer_decorator(permission="read")
        def post(layer, lid=None):
            data = request.get_json(force=True)
            exported_json = layer.export_geojson(
                filter_ids=data.get('filter_ids'))
            mem = BytesIO()
            mem.write(json.dumps(exported_json, indent=4).encode('utf-8'))
            mem.seek(0)
            return send_file(mem, mimetype='text/plain', as_attachment=True, attachment_filename='export.geojson')
        return post(lid=lid)
