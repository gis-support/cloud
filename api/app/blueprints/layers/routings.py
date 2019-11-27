#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, make_response
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, cloud_decorator, create_mvt_tile, layer_decorator
from app.helpers.cloud import Cloud
from app.helpers.layer import Layer
from shapely.geometry import shape
from osgeo import osr
from osgeo import ogr
import tempfile
import os.path as op

mod_layers = Blueprint("layers", __name__)


GDAL_TO_PG = {
    "String": "character varying",
    "Integer": "integer",
    "Real": "real",
    "DateTime": "timestamp without time zone",
    "Date": "timestamp without time zone",
    "Integer64": "integer"
}


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
        if not name:
            return jsonify({"error": "name is required"}), 401
        if cloud.layer_exists(name):
            return jsonify({"error": "layer already exists"}), 401
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
        try:
            epsg = layer.GetSpatialRef().GetAuthorityCode(None)
        except:
            epsg = request.form.get("epsg", "4326")
        transform = None
        if epsg != "4326":
            inSpatialRef = osr.SpatialReference()
            inSpatialRef.ImportFromEPSG(int(epsg))
            outSpatialRef = osr.SpatialReference()
            outSpatialRef.ImportFromEPSG(4326)
            transform = osr.CoordinateTransformation(
                inSpatialRef, outSpatialRef)
        ldefn = layer.GetLayerDefn()
        test_geom_type_feature = layer.GetNextFeature()
        layer.ResetReading()
        fields = [{
            "name": "geometry",
            "type": "geometry({}, 4326)".format(test_geom_type_feature.GetGeometryRef().GetGeometryName())
        }]
        for n in range(ldefn.GetFieldCount()):
            fdefn = ldefn.GetFieldDefn(n)
            fields.append({
                'name': fdefn.name,
                'type': GDAL_TO_PG[fdefn.GetTypeName()],
            })
        with current_app._db.atomic() as transaction:
            cloud = Cloud({"app": current_app, "user": request.user})
            cloud.create_layer(name, fields)
            with tempfile.SpooledTemporaryFile(mode='w') as tfile:
                columns = list(map(lambda f: f['name'], fields))
                count_features = 0
                for feature in layer:
                    the_geom = feature.GetGeometryRef()
                    if transform:
                        the_geom.Transform(transform)
                    feature_string = ''
                    if len(columns) == 1:
                        # W przypadku braku atrybutów
                        feature_string += 'SRID=4326;%s\n' % feature.GetGeometryRef().ExportToWkt()
                    else:
                        for idx, column in enumerate(columns):
                            # Pierwszy wiersz to geometria
                            if idx == 0:
                                feature_string += 'SRID=4326;%s\t' % feature.GetGeometryRef().ExportToWkt()
                            elif idx + 1 != len(columns):
                                feature_string += '%s\t' % feature.GetField(
                                    column)
                            else:
                                feature_string += '%s\n' % feature.GetField(
                                    column)
                    count_features += 1
                    tfile.write(feature_string)
                tfile.seek(0)
                cur = current_app._db.cursor()
                cur.copy_from(tfile, '"{}"'.format(name), null='None', columns=list(
                    map(lambda c: '"{}"'.format(c), columns)))
        layer = Layer({"app": current_app, "user": request.user, "name": name})
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
        @layer_decorator(permission="owner")
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
                    layer.change_name(layer_name)
                    return jsonify({"settings": layer.lid})
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
            try:
                layer.add_column(column_name, column_type)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            return jsonify({"settings": f"{column_name} added"})
        return post(lid=lid)


@mod_layers.route('/mvt/<int:z>/<int:x>/<int:y>', methods=['GET'])
def tiles(z=0, x=0, y=0):
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "invalid layer name"})
    tile = create_mvt_tile(z, x, y, name)
    if not tile:
        return ('', 204)
    response = make_response(tile)
    response.headers['Content-Type'] = "application/octet-stream"
    return response
