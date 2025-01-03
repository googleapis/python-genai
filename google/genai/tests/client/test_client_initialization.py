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

from ... import _api_client as api_client
from ... import _replay_api_client as replay_api_client
from ... import Client


def test_ml_dev_from_env(monkeypatch):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  client = Client()

  assert not client.models.api_client.vertexai
  assert client.models.api_client.api_key == api_key
  assert isinstance(client.models.api_client, api_client.ApiClient)


def test_ml_dev_from_constructor():
  api_key = "google_api_key"

  client = Client(api_key=api_key)

  assert not client.models.api_client.vertexai
  assert client.models.api_client.api_key == api_key


def test_constructor_with_http_options():
  mldev_http_options = {
      "api_version": "v1mldev",
      "base_url": "https://placeholder-fake-url.com/",
      "headers": {"X-Custom-Header": "custom_value_mldev"},
      "timeout": 10.0,
  }
  vertexai_http_options = {
      "api_version": "v1vertexai",
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
      "headers": {"X-Custom-Header": "custom_value_vertexai"},
      "timeout": 11.0,
  }

  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models.api_client.vertexai
  assert (
      mldev_client.models.api_client.get_read_only_http_options()["base_url"]
      == "https://placeholder-fake-url.com/"
  )
  assert (
      mldev_client.models.api_client.get_read_only_http_options()["api_version"]
      == "v1mldev"
  )

  assert mldev_client.models.api_client.get_read_only_http_options()["headers"][
      "X-Custom-Header"] == "custom_value_mldev"

  assert mldev_client.models.api_client.get_read_only_http_options()[
      "timeout"
  ] == 10.0

  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
      http_options=vertexai_http_options,
  )
  assert vertexai_client.models.api_client.vertexai
  assert (
      vertexai_client.models.api_client.get_read_only_http_options()["base_url"]
      == "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
  )
  assert (
      vertexai_client.models.api_client.get_read_only_http_options()[
          "api_version"
      ]
      == "v1vertexai"
  )
  assert (
      vertexai_client.models.api_client.get_read_only_http_options()["headers"][
          "X-Custom-Header"
      ]
      == "custom_value_vertexai"
  )

  assert vertexai_client.models.api_client.get_read_only_http_options()[
      "timeout"
  ] == 11.0


def test_constructor_with_response_payload_in_http_options():
  mldev_http_options = {
      "api_version": "v1",
      "base_url": "https://placeholder-fake-url.com/",
      "headers": {"X-Custom-Header": "custom_value"},
      "response_payload": {},
  }
  vertexai_http_options = {
      "api_version": "v1",
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/"
      ),
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


def test_vertexai_from_env_1(monkeypatch):
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  client = Client()

  assert client.models.api_client.vertexai
  assert client.models.api_client.project == project_id
  assert client.models.api_client.location == location


def test_vertexai_from_env_true(monkeypatch):
  project_id = "fake_project_id"
  location = "fake-location"
  monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  client = Client()

  assert client.models.api_client.vertexai
  assert client.models.api_client.project == project_id
  assert client.models.api_client.location == location


def test_vertexai_from_constructor():
  project_id = "fake_project_id"
  location = "fake-location"

  client = Client(
      vertexai=True,
      project=project_id,
      location=location,
  )

  assert client.models.api_client.vertexai
  assert client.models.api_client.project == project_id
  assert client.models.api_client.location == location
  assert isinstance(client.models.api_client, api_client.ApiClient)


def test_invalid_vertexai_constructor():
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


def test_replay_client_ml_dev_from_env(monkeypatch, use_vertex: bool):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")
  api_type = "vertex" if use_vertex else "mldev"
  monkeypatch.setenv("GOOGLE_GENAI_REPLAY_ID", "test_replay_id." + api_type)
  monkeypatch.setenv("GOOGLE_GENAI_REPLAYS_DIRECTORY", "test_replay_data")

  client = Client()

  assert not client.models.api_client.vertexai
  assert client.models.api_client.api_key == api_key
  assert isinstance(client.models.api_client, replay_api_client.ReplayApiClient)


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

  assert client.models.api_client.vertexai
  assert client.models.api_client.project == project_id
  assert client.models.api_client.location == location
  assert isinstance(client.models.api_client, replay_api_client.ReplayApiClient)


def test_change_client_mode_from_env(monkeypatch, use_vertex: bool):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")

  client1 = Client()
  assert isinstance(
      client1.models.api_client, replay_api_client.ReplayApiClient
  )

  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", None)

  client2 = Client()
  assert isinstance(client2.models.api_client, api_client.ApiClient)
