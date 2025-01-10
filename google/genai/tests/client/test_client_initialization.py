# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Tests for client initialization."""

import google.auth
from google.auth import credentials
import pytest

from ... import _api_client as api_client
from ... import _replay_api_client as replay_api_client
from ... import Client


def test_ml_dev_from_env(monkeypatch):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_ml_dev_from_constructor():
  api_key = "google_api_key"

  client = Client(api_key=api_key)

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key


def test_constructor_with_http_options():
  mldev_http_options = {
      "api_version": "v1main",
      "base_url": "https://placeholder-fake-url.com/",
      "headers": {"X-Custom-Header": "custom_value_mldev"},
      "timeout": 10.0,
  }
  vertexai_http_options = {
      "api_version": "v1",
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
      "headers": {"X-Custom-Header": "custom_value_vertexai"},
      "timeout": 11.0,
  }

  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://placeholder-fake-url.com/"
  )
  assert (
      mldev_client.models._api_client.get_read_only_http_options()[
          "api_version"
      ]
      == "v1main"
  )

  assert (
      mldev_client.models._api_client.get_read_only_http_options()["headers"][
          "X-Custom-Header"
      ]
      == "custom_value_mldev"
  )

  assert (
      mldev_client.models._api_client.get_read_only_http_options()["timeout"]
      == 10.0
  )

  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
      http_options=vertexai_http_options,
  )
  assert vertexai_client.models._api_client.vertexai
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "base_url"
      ]
      == "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
  )
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "api_version"
      ]
      == "v1"
  )
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "headers"
      ]["X-Custom-Header"]
      == "custom_value_vertexai"
  )

  assert (
      vertexai_client.models._api_client.get_read_only_http_options()["timeout"]
      == 11.0
  )


def test_constructor_with_response_payload_in_http_options():
  mldev_http_options = {
      "api_version": "v1",
      "base_url": "https://placeholder-fake-url.com/",
      "headers": {"X-Custom-Header": "custom_value"},
      "response_payload": {},
  }
  vertexai_http_options = {
      "api_version": "v1",
      "base_url": "https://{self.location}-aiplatform.googleapis.com/",
      "headers": {"X-Custom-Header": "custom_value"},
      "response_payload": {},
  }

  # Expect value error when response_payload in http_options is set for mldev
  # client.
  try:
    _ = Client(api_key="google_api_key", http_options=mldev_http_options)
  except ValueError as e:
    assert "Setting response_payload in http_options is not supported." in str(
        e
    )

  # Expect value error when response_payload in http_options is set for
  # vertexai client.
  try:
    _ = Client(
        vertexai=True,
        project="fake_project_id",
        location="fake-location",
        http_options=vertexai_http_options,
    )
  except ValueError as e:
    assert "Setting response_payload in http_options is not supported." in str(
        e
    )


def test_constructor_with_invalid_http_options_key():
  mldev_http_options = {
      "invalid_version_key": "v1",
      "base_url": "https://placeholder-fake-url.com/",
      "headers": {"X-Custom-Header": "custom_value"},
  }
  vertexai_http_options = {
      "api_version": "v1",
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
      "invalid_header_key": {"X-Custom-Header": "custom_value"},
  }

  # Expect value error when HTTPOptions is provided as a dict and contains
  # an invalid key.
  try:
    _ = Client(api_key="google_api_key", http_options=mldev_http_options)
  except Exception as e:
    assert isinstance(e, ValueError)
    assert "Invalid http_options" in str(e)

  # Expect value error when HTTPOptions is provided as a dict and contains
  # an invalid key.
  try:
    _ = Client(
        vertexai=True,
        project="fake_project_id",
        location="fake-location",
        http_options=vertexai_http_options,
    )
  except Exception as e:
    assert isinstance(e, ValueError)
    assert "Invalid http_options" in str(e)


def test_constructor_with_http_options_as_pydantic_type():
  mldev_http_options = api_client.HttpOptions(
      api_version="v1",
      base_url="https://placeholder-fake-url.com/",
      headers={"X-Custom-Header": "custom_value"},
  )
  vertexai_http_options = api_client.HttpOptions(
      api_version="v1",
      base_url=(
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
      headers={"X-Custom-Header": "custom_value"},
  )

  # Test http_options for mldev client.
  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == mldev_http_options.base_url
  )
  assert (
      mldev_client.models._api_client.get_read_only_http_options()[
          "api_version"
      ]
      == mldev_http_options.api_version
  )

  assert (
      mldev_client.models._api_client.get_read_only_http_options()["headers"][
          "X-Custom-Header"
      ]
      == mldev_http_options.headers["X-Custom-Header"]
  )

  # Test http_options for vertexai client.
  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
      http_options=vertexai_http_options,
  )
  assert vertexai_client.models._api_client.vertexai
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "base_url"
      ]
      == vertexai_http_options.base_url
  )
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "api_version"
      ]
      == vertexai_http_options.api_version
  )
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "headers"
      ]["X-Custom-Header"]
      == vertexai_http_options.headers["X-Custom-Header"]
  )


def test_vertexai_from_env_1(monkeypatch):
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  client = Client()

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location


def test_vertexai_from_env_true(monkeypatch):
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  client = Client()

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location


def test_vertexai_from_constructor():
  project_id = "fake_project_id"
  location = "fake-location"

  client = Client(
      vertexai=True,
      project=project_id,
      location=location,
  )

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_invalid_vertexai_constructor_empty(monkeypatch):
  with pytest.raises(ValueError):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    def mock_auth_default():
      return None, None

    monkeypatch.setattr(google.auth, "default", mock_auth_default)
    Client(vertexai=True)


def test_invalid_mldev_constructor_empty(monkeypatch):
  with pytest.raises(ValueError):
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    Client()


def test_invalid_vertexai_constructor1():
  project_id = "fake_project_id"
  location = "fake-location"
  api_key = "fake-api_key"
  try:
    Client(
        vertexai=True,
        project=project_id,
        location=location,
        api_key=api_key,
    )
  except Exception as e:
    assert isinstance(e, ValueError)


def test_invalid_vertexai_constructor2():
  creds = credentials.AnonymousCredentials()
  api_key = "fake-api_key"
  with pytest.raises(ValueError):
    Client(
        vertexai=True,
        credentials=creds,
        api_key=api_key,
    )


def test_vertexai_explicit_arg_precedence1(monkeypatch):
  project_id = "constructor_project_id"
  location = "constructor-location"

  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "env_project_id")
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "env_location")
  monkeypatch.setenv("GOOGLE_API_KEY", "")

  client = Client(
      vertexai=True,
      project=project_id,
      location=location,
  )

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert not client.models._api_client.api_key
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_vertexai_explicit_arg_precedence2(monkeypatch):
  api_key = "constructor_apikey"

  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_API_KEY", "env_api_key")

  client = Client(
      vertexai=True,
      api_key=api_key,
  )

  assert client.models._api_client.vertexai
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_invalid_mldev_constructor():
  project_id = "fake_project_id"
  location = "fake-location"
  api_key = "fake-api_key"
  try:
    Client(
        project=project_id,
        location=location,
        api_key=api_key,
    )
  except Exception as e:
    assert isinstance(e, ValueError)


def test_mldev_explicit_arg_precedence(monkeypatch):
  api_key = "constructor_api_key"

  monkeypatch.setenv("GOOGLE_API_KEY", "env_api_key")

  client = Client(api_key=api_key)

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_replay_client_ml_dev_from_env(monkeypatch, use_vertex: bool):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")
  api_type = "vertex" if use_vertex else "mldev"
  monkeypatch.setenv("GOOGLE_GENAI_REPLAY_ID", "test_replay_id." + api_type)
  monkeypatch.setenv("GOOGLE_GENAI_REPLAYS_DIRECTORY", "test_replay_data")

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(
      client.models._api_client, replay_api_client.ReplayApiClient
  )


def test_replay_client_vertexai_from_env(monkeypatch, use_vertex: bool):
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")
  api_type = "vertex" if use_vertex else "mldev"
  monkeypatch.setenv("GOOGLE_GENAI_REPLAY_ID", "test_replay_id." + api_type)
  monkeypatch.setenv("GOOGLE_GENAI_REPLAYS_DIRECTORY", "test_replay_data")

  client = Client()

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert isinstance(
      client.models._api_client, replay_api_client.ReplayApiClient
  )


def test_change_client_mode_from_env(monkeypatch, use_vertex: bool):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")

  client1 = Client()
  assert isinstance(
      client1.models._api_client, replay_api_client.ReplayApiClient
  )

  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", None)

  client2 = Client()
  assert isinstance(client2.models._api_client, api_client.ApiClient)


def test_vertexai_apikey_from_constructor(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(api_key=api_key, vertexai=True)

  assert client.models._api_client.vertexai
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert client.models._api_client.api_key == api_key
  assert "aiplatform" in client._api_client._http_options["base_url"]
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_vertexai_apikey_from_env(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options["base_url"]
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_vertexai_apikey_invalid_constructor1():
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  project_id = "fake_project_id"
  location = "fake-location"

  with pytest.raises(ValueError):
    Client(
        api_key=api_key,
        project=project_id,
        location=location,
        vertexai=True,
    )


def test_vertexai_apikey_combo1(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)
  monkeypatch.setenv("GOOGLE_API_KEY", "")

  # Explicit api_key takes precedence over implicit project/location.
  client = Client(vertexai=True, api_key=api_key)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options["base_url"]
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_vertexai_apikey_combo2(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  # Explicit project/location takes precedence over implicit api_key.
  client = Client(vertexai=True, project=project_id, location=location)

  assert client.models._api_client.vertexai
  assert not client.models._api_client.api_key
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert "aiplatform" in client._api_client._http_options["base_url"]
  assert isinstance(client.models._api_client, api_client.ApiClient)


def test_vertexai_apikey_combo3(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  project_id = "fake_project_id"
  location = "fake-location"
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  # Implicit project/location takes precedence over implicit api_key.
  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert not client.models._api_client.api_key
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert "aiplatform" in client._api_client._http_options["base_url"]
  assert isinstance(client.models._api_client, api_client.ApiClient)
