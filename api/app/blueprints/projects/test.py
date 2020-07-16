import json
from copy import deepcopy

import pytest
from flask import Response
from flask.testing import FlaskClient

from app.tests.utils import BaseTest


@pytest.mark.projects
class TestProjects(BaseTest):

    def create_project(self, client: FlaskClient, data: dict, token: str) -> Response:
        query_string = {"token": token}
        response = client.post("/api/projects", data=json.dumps(data), query_string=query_string)
        return response

    def get_projects(self, client: FlaskClient, token: str) -> Response:
        query_string = {"token": token}
        response = client.get("/api/projects", query_string=query_string)
        return response

    def get_project(self, client: FlaskClient, project_id: int, token: str) -> Response:
        query_string = {"token": token}
        response = client.get(f"/api/projects/{project_id}", query_string=query_string)
        return response

    def edit_project(self, client: FlaskClient, project_id: int, data: dict, token: str) -> Response:
        query_string = {"token": token}
        response = client.put(f"/api/projects/{project_id}", data=json.dumps(data), query_string=query_string)
        return response

    def delete_project(self, client: FlaskClient, project_id: int, token: str) -> Response:
        query_string = {"token": token}
        response = client.delete(f"/api/projects/{project_id}", query_string=query_string)
        return response

    def change_layer_permission(self, client: FlaskClient, layer_id: str, permission: str, user_name: str, token: str) -> Response:
        query_string = {"token": token}
        data = {"permission": permission, "user": user_name}
        response = client.put(f"/api/permissions/{layer_id}", data=json.dumps(data), query_string=query_string)
        return response

    def test_create_valid_project(self, client: FlaskClient):
        token = self.get_token(client)

        lid = self.add_geojson_prg(client, token)

        data = {
            "name": "name",
            "active_layer_id": lid,
            "map_center": {
                "coordinates": [
                  21,
                  52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        result = self.create_project(client, data, token)
        assert result.status_code == 201
        assert isinstance(result.json["data"], int)

    def test_create_project_no_permission_to_active_layer(self, client: FlaskClient):
        token = self.get_token(client)

        lid = self.add_geojson_prg(client, token)

        data = {
            "name": "name",
            "active_layer_id": lid,
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        user_name, user_password = self.create_user(client)
        other_token = self.get_token(client, user_name, user_password)

        result = self.create_project(client, data, other_token)
        assert result.status_code == 403
        assert result.json["error"] == f"permission denied to layer {lid}"

    def test_create_project_no_permission_to_additional_layer(self, client: FlaskClient):
        token = self.get_token(client)

        user_name, user_password = self.create_user(client)
        other_token = self.get_token(client, user_name, user_password)

        active_layer_id = self.add_geojson_prg(client, other_token, name="layer1")
        additional_layer_id = self.add_geojson_prg(client, token, name="layer2")

        data = {
            "name": "name",
            "active_layer_id": active_layer_id,
            "additional_layers_ids": [additional_layer_id],
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        result = self.create_project(client, data, other_token)
        assert result.status_code == 403
        assert result.json["error"] == f"permission denied to layer {additional_layer_id}"

    def test_create_project_non_existent_active_layer(self, client: FlaskClient):
        token = self.get_token(client)

        layer_id = "id"

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        result = self.create_project(client, data, token)
        assert result.status_code == 400
        assert result.json["error"] == f"layer {layer_id} does not exist"

    def test_get_projects(self, client: FlaskClient):
        token = self.get_token(client)

        layer_id = self.add_geojson_prg(client, token)

        data_1 = {
            "name": "name_1",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        data_2 = {
            "name": "name_2",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    41.0,
                    33.0
                ],
                "type": "Point"
            },
            "map_zoom": 15,
        }

        project_1_id = self.create_project(client, data_1, token).json["data"]
        project_2_id = self.create_project(client, data_2, token).json["data"]

        expected_data_1 = deepcopy(data_1)
        expected_data_1["id"] = project_1_id
        expected_data_1["permission_to_each_additional_layer"] = True
        expected_data_1["permission_to_active_layer"] = True
        expected_data_1["additional_layers_ids"] = []

        expected_data_2 = deepcopy(data_2)
        expected_data_2["id"] = project_2_id
        expected_data_2["permission_to_each_additional_layer"] = True
        expected_data_2["permission_to_active_layer"] = True
        expected_data_2["additional_layers_ids"] = []

        expected_data = [expected_data_1, expected_data_2]

        result = self.get_projects(client, token)
        assert result.status_code == 200

        actual_data = result.json["data"]
        actual_data = sorted(actual_data, key=lambda x: x["id"])

        assert actual_data == expected_data

    def test_get_projects_permission_to_layers_revoked(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        active_layer_id = self.add_geojson_prg(client, token_2, name="layer1")
        self.change_layer_permission(client, active_layer_id, "read", user_1_name, token_2)

        additional_layer_id = self.add_geojson_prg(client, token_2, name="layer2")
        self.change_layer_permission(client, additional_layer_id, "read", user_1_name, token_2)

        data = {
            "name": "name",
            "active_layer_id": active_layer_id,
            "additional_layers_ids": [additional_layer_id],
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        self.create_project(client, data, token_1)

        self.change_layer_permission(client, active_layer_id, "", user_1_name, token_2)
        self.change_layer_permission(client, additional_layer_id, "", user_1_name, token_2)

        result = self.get_projects(client, token_1)
        assert result.status_code == 200
        actual_data = result.json["data"][0]
        assert actual_data["permission_to_active_layer"] is False
        assert actual_data["permission_to_each_additional_layer"] is False

    def test_get_project(self, client: FlaskClient):
        token = self.get_token(client)

        layer_id = self.add_geojson_prg(client, token)

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token).json["data"]

        expected_data = deepcopy(data)
        expected_data["id"] = project_id
        expected_data["permission_to_each_additional_layer"] = True
        expected_data["additional_layers_ids"] = []

        result = self.get_project(client, project_id, token)
        assert result.status_code == 200

        actual_data = result.json["data"]
        assert actual_data == expected_data

    def test_get_nonexistent_project(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.get_project(client, 0, token)
        assert result.status_code == 404
        assert result.json["error"] == "project does not exist"

    def test_get_project_permission_to_active_layer_revoked(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        active_layer_id = self.add_geojson_prg(client, token_2, name="layer1")
        self.change_layer_permission(client, active_layer_id, "read", user_1_name, token_2)

        data = {
            "name": "name",
            "active_layer_id": active_layer_id,
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token_1).json["data"]

        self.change_layer_permission(client, active_layer_id, "", user_1_name, token_2)

        result = self.get_project(client, project_id, token_1)
        assert result.status_code == 403
        assert result.json["error"] == "permission denied for project`s active layer"

    def test_get_project_permission_to_additional_layer_revoked(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        active_layer_id = self.add_geojson_prg(client, token_1, name="layer1")

        additional_layer_id = self.add_geojson_prg(client, token_2, name="layer2")
        self.change_layer_permission(client, additional_layer_id, "read", user_1_name, token_2)

        data = {
            "name": "name",
            "active_layer_id": active_layer_id,
            "additional_layers_ids": [additional_layer_id],
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token_1).json["data"]

        self.change_layer_permission(client, additional_layer_id, "", user_1_name, token_2)

        result = self.get_project(client, project_id, token_1)
        assert result.status_code == 200
        assert result.json["data"]["permission_to_each_additional_layer"] is False

    def test_delete_nonexistent_project(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.delete_project(client, 0, token)
        assert result.status_code == 404
        assert result.json["error"] == "project does not exist"

    def test_delete_project(self, client: FlaskClient):
        token = self.get_token(client)

        layer_id = self.add_geojson_prg(client, token)

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token).json["data"]

        result_delete = self.delete_project(client, project_id, token)
        assert result_delete.status_code == 204

        result_get = self.get_project(client, project_id, token)
        assert result_get.status_code == 404

    def test_delete_other_users_project(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        layer_id = self.add_geojson_prg(client, token_1)

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token_1).json["data"]

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        result = self.delete_project(client, project_id, token_2)
        assert result.status_code == 403
        assert result.json["error"] == "permission denied to other users projects"

    def test_edit_project(self, client: FlaskClient):
        token = self.get_token(client)

        layer_id = self.add_geojson_prg(client, token)

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token).json["data"]

        update_data = {
            "name": "name_2",
            "map_center": {
                "coordinates": [
                    21.1,
                    52.1
                ],
                "type": "Point"
            }
        }

        result_edit = self.edit_project(client, project_id, update_data, token)
        assert result_edit.status_code == 204

        result_get = self.get_project(client, project_id, token)
        actual_data = result_get.json["data"]

        expected_data = deepcopy(data)
        expected_data.update(update_data)
        expected_data["id"] = project_id
        expected_data["permission_to_each_additional_layer"] = True
        expected_data["additional_layers_ids"] = []

        assert actual_data == expected_data

    def test_edit_nonexistent_project(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.edit_project(client, 0, {}, token)
        assert result.status_code == 404
        assert result.json["error"] == "project does not exist"

    def test_edit_other_users_project(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        layer_id = self.add_geojson_prg(client, token_1)

        data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                    21.0,
                    52.0
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token_1).json["data"]

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        result = self.edit_project(client, project_id, {}, token_2)
        assert result.status_code == 403
        assert result.json["error"] == "permission denied to other users projects"

    def test_edit_project_no_permission_to_layer(self, client: FlaskClient):
        user_1_name, user_1_password = self.create_user(client)
        token_1 = self.get_token(client, user_1_name, user_1_password)

        user_2_name, user_2_password = self.create_user(client)
        token_2 = self.get_token(client, user_2_name, user_2_password)

        layer_1 = self.add_geojson_prg(client, token_1, name="layer1")

        data = {
            "name": "name",
            "active_layer_id": layer_1,
            "map_center": {
                "coordinates": [
                    21,
                    52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
        }

        project_id = self.create_project(client, data, token_1).json["data"]

        layer_2 = self.add_geojson_prg(client, token_2, name="layer2")
        update_data = {
            "active_layer_id": layer_2
        }

        result = self.edit_project(client, project_id, update_data, token_1)
        assert result.status_code == 403
        assert result.json["error"] == f"permission denied to layer {layer_2}"
