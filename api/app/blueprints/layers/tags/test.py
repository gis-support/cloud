import json
from copy import deepcopy

import pytest
from flask import Response
from flask.testing import FlaskClient

from app.blueprints.layers.tags.models import Tag
from app.tests.utils import BaseTest


@pytest.mark.layers
@pytest.mark.layers_tags
class TestTags:

    def create_mock_tag(self, name="nazwa_taga", color="czerowny") -> Tag:
        return Tag(name=name, color=color)

    def test_does_tag_with_name_exist(self, app_request_context):
        name = "nazwa"
        result = Tag.does_tag_with_name_exist(name)

        assert result is False

        mock_1 = self.create_mock_tag(name=name)
        mock_1.save()

        result = Tag.does_tag_with_name_exist(name)
        assert result is True

    def test_does_tag_with_name_exist_except_self(self, app_request_context):
        name = "nazwa"

        mock_1 = self.create_mock_tag()
        mock_1.save()

        result = Tag.does_tag_with_name_exist(name, except_=mock_1)

        assert result is False


@pytest.mark.layers
@pytest.mark.layers_tags
class TestTagsEndpoints(BaseTest):

    valid_tag_post_data = {
        "name": "nazwa taga",
        "color": "#123456"
    }

    def post_tag(self, client: FlaskClient, token: str = None, data: dict = None) -> Response:
        if data is None:
            data = self.valid_tag_post_data
        if token is None:
            token = self.get_token(client)

        result = client.post("/api/tags", query_string={"token": token}, data=json.dumps(data))
        return result

    def get_tags(self, client: FlaskClient, token: str = None) -> Response:
        if token is None:
            token = self.get_token(client)

        result = client.get("/api/tags", query_string={"token": token})
        return result

    def edit_tag(self, client: FlaskClient, tag_id: int, data: dict, token: str) -> Response:
        result = client.put(f"/api/tags/{tag_id}", query_string={"token": token}, data=json.dumps(data))
        return result

    def delete_tag(self, client: FlaskClient, tag_id: int, token: str = None) -> Response:
        if token is None:
            token = self.get_token(client)

        result = client.delete(f"/api/tags/{tag_id}", query_string={"token": token})
        return result

    def post_layer_tag(self, client: FlaskClient, data: dict, token: str = None) -> Response:
        if token is None:
            token = self.get_token(client)
        query_string = {"token": token}

        query_string.update(data)

        result = client.post("/api/tags/layers", query_string=query_string)
        return result

    def delete_layer_tag(self, client: FlaskClient, data: dict, token: str = None) -> Response:
        if token is None:
            token = self.get_token(client)
        query_string = {"token": token}

        query_string.update(data)

        result = client.delete("/api/tags/layers", query_string=query_string)
        return result

    def get_layers(self, client: FlaskClient, token: str):
        return client.get("/api/layers", query_string={"token": token})

    def rename_layer(self, client: FlaskClient, layer_id: str, new_name: str, token: str = None) -> str:
        if token is None:
            token = self.get_token(client)
        query_string = {"token": token}

        data = {"layer_name": new_name}

        return client.post(f"/api/layers/{layer_id}/settings", data=json.dumps(data), query_string=query_string).json["settings"]

    def test_post_tag_valid(self, client: FlaskClient):
        result = self.post_tag(client)

        assert result.status_code == 201
        assert isinstance(result.json["data"], int)

    def test_post_tag_invalid(self, client: FlaskClient):
        result = self.post_tag(client, data={})

        assert result.status_code == 400

        actual_error_message = result.json["error"]
        expected_error_message = "invalid attributes - ('name', 'color') are required"

        assert actual_error_message == expected_error_message

    def test_post_tag_bad_token(self, client: FlaskClient):
        result = self.post_tag(client, token="")

        assert result.status_code == 403

        actual_error_message = result.json["error"]
        expected_error_message = "token required"

        assert actual_error_message == expected_error_message

    def test_post_tag_duplicate_name(self, client: FlaskClient):
        data = self.valid_tag_post_data
        tag_name = data["name"]

        result = self.post_tag(client, data=data)
        assert result.status_code == 201

        result = self.post_tag(client, data=data)
        assert result.status_code == 400

        actual_error_message = result.json["error"]
        expected_error_message = f"tag with name '{tag_name}' already exists"

        assert actual_error_message == expected_error_message

    def test_get_tags_empty(self, client: FlaskClient):
        result = self.get_tags(client)

        assert result.status_code == 200
        assert result.json == {"data": []}

    def test_get_tags_bad_token(self, client: FlaskClient):
        result = self.get_tags(client, token="")

        assert result.status_code == 403

        actual_error_message = result.json["error"]
        expected_error_message = "token required"

        assert actual_error_message == expected_error_message

    def test_post_and_get_tags(self, client: FlaskClient):
        data_1 = {"name": "tag 1", "color": "#123456"}
        result_1 = self.post_tag(client, data=data_1)
        tag_1_id = result_1.json["data"]

        data_2 = {"name": "tag 2", "color": "#123456"}
        result_2 = self.post_tag(client, data=data_2)
        tag_2_id = result_2.json["data"]

        result = self.get_tags(client)

        assert result.status_code == 200

        actual_data = result.json["data"]
        expected_data = [
            {
                **data_1,
                "id": tag_1_id
            },
            {
                **data_2,
                "id": tag_2_id
            }
        ]

        assert actual_data == expected_data

    def test_create_and_edit_tag(self, client: FlaskClient):
        token = self.get_token(client)

        tag_data = {"name": "name", "color": "color"}
        tag_id = self.post_tag(client, token, tag_data).json["data"]

        new_data = {"name": "new_name", "color": "new_color"}
        self.edit_tag(client, tag_id, new_data, token)

        tags = self.get_tags(client).json["data"]

        expected_data = deepcopy(new_data)
        expected_data["id"] = tag_id
        assert tags[0] == expected_data

    def test_try_set_name_to_already_taken_by_other_tag(self, client: FlaskClient):
        token = self.get_token(client)

        tag_1_data = {"name": "name", "color": "color"}
        self.post_tag(client, token, tag_1_data)

        tag_2_data = {"name": "name_2", "color": "color"}
        tag_2_id = self.post_tag(client, token, tag_2_data).json["data"]

        new_data_2 = {"name": "name", "color": "new_color"}
        result = self.edit_tag(client, tag_2_id, new_data_2, token)

        assert result.status_code == 400

        actual_error_message = result.json["error"]
        expected_error_message = f"tag with name 'name' already exists"

        assert actual_error_message == expected_error_message

    def test_try_set_name_to_same(self, client: FlaskClient):
        token = self.get_token(client)

        tag_data = {"name": "name", "color": "color"}
        tag_id = self.post_tag(client, token, tag_data).json["data"]

        new_data = {"name": "name", "color": "new_color"}
        self.edit_tag(client, tag_id, new_data, token)

        tags = self.get_tags(client).json["data"]

        expected_data = deepcopy(new_data)
        expected_data["id"] = tag_id
        assert tags[0] == expected_data

    def test_delete_tag_bad_token(self, client: FlaskClient):
        result = self.delete_tag(client, 0, token="")

        assert result.status_code == 403

        actual_error_message = result.json["error"]
        expected_error_message = "token required"

        assert actual_error_message == expected_error_message

    def test_delete_non_existent_tag(self, client: FlaskClient):
        tag_id = 0
        result = self.delete_tag(client, tag_id)

        assert result.status_code == 404

        expected_error_message = f"tag with ID '{tag_id}' does not exist"
        actual_error_message = result.json["error"]

        assert expected_error_message == actual_error_message

    def test_create_and_delete_tag(self, client: FlaskClient):
        result = self.post_tag(client)
        tag_id = result.json["data"]

        result = self.delete_tag(client, tag_id)
        assert result.status_code == 204

        result = self.delete_tag(client, tag_id)
        assert result.status_code == 404

    def test_get_layers_with_tags(self, client: FlaskClient):
        token = self.get_token(client)
        layer_id = self.add_geojson_prg(client, token)

        tag_id = self.post_tag(client).json["data"]

        tags = self.get_tags(client).json["data"]

        layer_tag_data = {"tag_id": tag_id, "layer_id": layer_id}
        self.post_layer_tag(client, layer_tag_data)

        layers = self.get_layers(client, token).json["layers"]

        assert layers[0]["tags"] == tags

    def test_get_tag_after_layer_name_change(self, client: FlaskClient):
        tag_data = {"name": "name", "color": "color"}

        token = self.get_token(client)
        layer_id = self.add_geojson_prg(client, token)

        tag_id = self.post_tag(client, data=tag_data).json["data"]
        layer_tag_data = {"tag_id": tag_id, "layer_id": layer_id}
        self.post_layer_tag(client, layer_tag_data)

        new_layer_id = self.rename_layer(client, layer_id, "new name", token)

        layers = self.get_layers(client, token)

        layer = layers.json["layers"][0]

        expected_data = deepcopy(tag_data)
        expected_data["id"] = tag_id

        assert layer["id"] == new_layer_id
        assert layer["tags"] == [expected_data]
