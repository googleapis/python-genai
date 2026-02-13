# Copyright 2025 Google LLC
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

import asyncio
import concurrent.futures
import logging
import os
import ssl
from unittest import mock

import certifi
import google.auth
from google.auth import credentials
import httpx
import pytest

from ... import _api_client as api_client
from ... import _base_url as base_url
from ... import _replay_api_client as replay_api_client
from ... import Client
from ... import types
try:
  import aiohttp
  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()


requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason="aiohttp is not installed, skipping test."
)


@pytest.fixture(autouse=True)
def reset_has_aiohttp():
  yield
  api_client.has_aiohttp = False


def test_ml_dev_from_gemini_env_only(monkeypatch):
  api_key = "gemini_api_key"
  monkeypatch.setenv("GEMINI_API_KEY", api_key)
  monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_ml_dev_from_gemini_env_with_google_env_empty(monkeypatch):
  api_key = "gemini_api_key"
  monkeypatch.setenv("GEMINI_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_API_KEY", "")

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_ml_dev_from_google_env_only(monkeypatch):
  api_key = "google_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.delenv("GEMINI_API_KEY", raising=False)

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_ml_dev_both_env_key_set(monkeypatch, caplog):
  caplog.set_level(logging.DEBUG, logger="google_genai._api_client")
  google_api_key = "google_api_key"
  gemini_api_key = "gemini_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", google_api_key)
  monkeypatch.setenv("GEMINI_API_KEY", gemini_api_key)

  client = Client()

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == google_api_key
  assert isinstance(client.models._api_client, api_client.BaseApiClient)
  assert (
      "Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY."
      in caplog.text
  )


def test_api_key_with_new_line(monkeypatch, caplog):
  caplog.set_level(logging.DEBUG, logger="google_genai._api_client")
  api_key = "gemini_api_key\r\n"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)

  client = Client()

  assert client.models._api_client.api_key == "gemini_api_key"


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
      "timeout": 10000,
  }
  vertexai_http_options = {
      "api_version": "v1",
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
      "headers": {"X-Custom-Header": "custom_value_vertexai"},
      "timeout": 11000,
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
      == 10000
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
      == 11000
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
    assert "invalid_version_key" in str(e)

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
    assert "invalid_header_key" in str(e)


def test_constructor_with_http_options_as_pydantic_type():
  mldev_http_options = types.HttpOptions(
      api_version="v1",
      base_url="https://placeholder-fake-url.com/",
      headers={"X-Custom-Header": "custom_value"},
  )
  vertexai_http_options = types.HttpOptions(
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
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_invalid_vertexai_constructor_empty(monkeypatch):
  with pytest.raises(ValueError):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")

    def mock_auth_default(scopes=None):
      return None, None

    monkeypatch.setattr(google.auth, "default", mock_auth_default)
    Client(vertexai=True)


def test_vertexai_constructor_empty_base_url_override(monkeypatch):
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_API_KEY", "")
  monkeypatch.setenv("GEMINI_API_KEY", "")

  def mock_auth_default(scopes=None):
    return None, None

  monkeypatch.setattr(google.auth, "default", mock_auth_default)
  # Including a base_url override skips the check for having proj/location or
  # api_key set.
  client = Client(vertexai=True, http_options={"base_url": "https://override.com/"})
  assert client.models._api_client.location is None


def test_invalid_mldev_constructor_empty(monkeypatch):
  with pytest.raises(ValueError):
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
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


def test_vertexai_default_location_to_global(monkeypatch):

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    project_id = "fake_project_id"
    client = Client(vertexai=True, project=project_id)
    assert client.models._api_client.location == "global"


def test_vertexai_default_location_to_global_with_credentials(monkeypatch):
  # Test case 1: When credentials are provided with project but no location
  creds = credentials.AnonymousCredentials()
  project_id = "fake_project_id"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.setenv("GOOGLE_API_KEY", "")
    client = Client(vertexai=True, credentials=creds, project=project_id)
    assert client.models._api_client.location == "global"
    assert client.models._api_client.project == project_id


def test_vertexai_default_location_to_global_with_explicit_project_and_env_apikey(
    monkeypatch,
):
  # Test case 2: When explicit project is provided and env api_key exists
  project_id = "explicit_project_id"
  api_key = "env_api_key"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    m.setenv("GOOGLE_API_KEY", api_key)
    client = Client(vertexai=True, project=project_id)
    # Explicit project takes precedence over implicit api_key
    assert client.models._api_client.location == "global"
    assert client.models._api_client.project == project_id
    assert not client.models._api_client.api_key


def test_vertexai_default_location_to_global_with_vertexai_base_url(
    monkeypatch,
):
  # Test case 4: When project and vertex base url are set
  project_id = "env_project_id"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.setenv("GOOGLE_CLOUD_PROJECT", project_id)
    client = Client(
        vertexai=True,
        http_options={'base_url': 'https://fake-url.googleapis.com'},
    )
    # Implicit project takes precedence over implicit api_key
    assert client.models._api_client.location == "global"
    assert client.models._api_client.project == project_id


def test_vertexai_default_location_to_global_with_arbitrary_base_url(
    monkeypatch,
):
  # Test case 5: When project and arbitrary base url (proxy) are set
  project_id = "env_project_id"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.setenv("GOOGLE_CLOUD_PROJECT", project_id)
    client = Client(
        vertexai=True,
        http_options={'base_url': 'https://fake-url.com'},
    )
    # Implicit project takes precedence over implicit api_key
    assert not client.models._api_client.location
    assert not client.models._api_client.project


def test_vertexai_default_location_to_global_with_env_project_and_env_apikey(
    monkeypatch,
):
  # Test case 3: When env project and env api_key both exist
  project_id = "env_project_id"
  api_key = "env_api_key"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.setenv("GOOGLE_CLOUD_PROJECT", project_id)
    m.setenv("GOOGLE_API_KEY", api_key)
    client = Client(vertexai=True)
    # Implicit project takes precedence over implicit api_key
    assert client.models._api_client.location == "global"
    assert client.models._api_client.project == project_id
    assert not client.models._api_client.api_key


def test_vertexai_no_default_location_when_location_explicitly_set(monkeypatch):
  # Verify that location is NOT defaulted to global when explicitly set
  project_id = "fake_project_id"
  location = "us-central1"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    client = Client(vertexai=True, project=project_id, location=location)
    assert client.models._api_client.location == location
    assert client.models._api_client.project == project_id


def test_vertexai_no_default_location_when_env_location_set(monkeypatch):
  # Verify that location is NOT defaulted to global when set via environment
  project_id = "fake_project_id"
  location = "us-west1"

  with monkeypatch.context() as m:
    m.setenv("GOOGLE_CLOUD_LOCATION", location)
    m.setenv("GOOGLE_CLOUD_PROJECT", project_id)
    client = Client(vertexai=True)
    assert client.models._api_client.location == location
    assert client.models._api_client.project == project_id


def test_vertexai_no_default_location_with_apikey_only(monkeypatch):
  # Verify that location is NOT set when using API key mode (no project)
  api_key = "vertexai_api_key"

  with monkeypatch.context() as m:
    m.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    m.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    m.setenv("GOOGLE_API_KEY", "")
    client = Client(vertexai=True, api_key=api_key)
    assert not client.models._api_client.location
    assert not client.models._api_client.project
    assert client.models._api_client.api_key == api_key


def test_vertexai_explicit_credentials(monkeypatch):
  creds = credentials.AnonymousCredentials()
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fake_project_id")
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "fake-location")
  monkeypatch.setenv("GOOGLE_API_KEY", "env_api_key")

  client = Client(
      vertexai=True,
      credentials=creds
  )

  assert client.models._api_client.vertexai
  assert client.models._api_client.project
  assert client.models._api_client.location
  assert not client.models._api_client.api_key
  assert client.models._api_client._credentials is creds
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


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
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


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
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


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


def test_mldev_explicit_arg_precedence(monkeypatch, caplog):
  caplog.set_level(logging.DEBUG, logger="google_genai._api_client")
  api_key = "constructor_api_key"

  monkeypatch.setenv("GOOGLE_API_KEY", "google_env_api_key")
  monkeypatch.setenv("GEMINI_API_KEY", "gemini_env_api_key")

  client = Client(api_key=api_key)

  assert not client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert isinstance(client.models._api_client, api_client.BaseApiClient)
  assert (
      "Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY."
      in caplog.text
  )


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
  monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "")

  client2 = Client()
  assert isinstance(client2.models._api_client, api_client.BaseApiClient)


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
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_vertexai_apikey_from_env_google_api_key_only(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GOOGLE_API_KEY", api_key)
  monkeypatch.delenv("GEMINI_API_KEY", raising=False)

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_vertexai_apikey_from_env_gemini_api_key_only(monkeypatch):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GEMINI_API_KEY", api_key)
  monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_vertexai_apikey_from_env_gemini_api_key_with_google_api_key_empty(
    monkeypatch,
):
  # Vertex AI Express mode uses API key on Vertex AI.
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GEMINI_API_KEY", api_key)
  monkeypatch.setenv("GOOGLE_API_KEY", "")

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_vertexai_apikey_from_env_both_api_keys(monkeypatch, caplog):
  caplog.set_level(logging.DEBUG, logger="google_genai._api_client")
  # Vertex AI Express mode uses API key on Vertex AI.
  google_api_key = "google_api_key"
  gemini_api_key = "vertexai_api_key"
  monkeypatch.setenv("GEMINI_API_KEY", gemini_api_key)
  monkeypatch.setenv("GOOGLE_API_KEY", google_api_key)

  # Due to proj/location taking precedence, need to clear proj/location env
  # variables.
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "")
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "")

  client = Client(vertexai=True)

  assert client.models._api_client.vertexai
  assert client.models._api_client.api_key == google_api_key
  assert not client.models._api_client.project
  assert not client.models._api_client.location
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)
  assert (
      "Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY."
      in caplog.text
  )


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
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


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
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


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
  assert "aiplatform" in client._api_client._http_options.base_url
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_vertexai_global_endpoint(monkeypatch):
  # Vertex AI uses global endpoint when location is global.
  project_id = "fake_project_id"
  location = "global"
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  client = Client(vertexai=True, location=location)

  assert client.models._api_client.vertexai
  assert client.models._api_client.project == project_id
  assert client.models._api_client.location == location
  assert client.models._api_client._http_options.base_url == (
      "https://aiplatform.googleapis.com/"
  )
  assert isinstance(client.models._api_client, api_client.BaseApiClient)


def test_client_logs_to_logger_instance(monkeypatch, caplog):
  caplog.set_level(logging.DEBUG, logger="google_genai._api_client")

  project_id = "fake_project_id"
  location = "fake-location"
  api_key = "vertexai_api_key"
  monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", project_id)
  monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", location)

  _ = Client(vertexai=True, api_key=api_key)

  assert "INFO" in caplog.text
  assert (
      "The user provided Vertex AI API key will take precedence" in caplog.text
  )


def test_client_ssl_context_implicit_initialization():
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(types.HttpOptions())
  )

  assert client_args["verify"]
  assert isinstance(client_args["verify"], ssl.SSLContext)
  try:
    import aiohttp  # pylint: disable=g-import-not-at-top

    async_client_args = api_client.BaseApiClient._ensure_aiohttp_ssl_ctx(
        types.HttpOptions()
    )
    assert async_client_args["ssl"]
    assert isinstance(async_client_args["ssl"], ssl.SSLContext)
  except ImportError:
    assert async_client_args["verify"]
    assert isinstance(async_client_args["verify"], ssl.SSLContext)


def test_client_ssl_context_explicit_initialization_same_args():
  ctx = ssl.create_default_context(
      cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
      capath=os.environ.get("SSL_CERT_DIR"),
  )

  options = types.HttpOptions(
      client_args={"verify": ctx}, async_client_args={"verify": ctx}
  )
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(options)
  )

  assert client_args["verify"] == ctx
  try:
    import aiohttp  # pylint: disable=g-import-not-at-top

    async_client_args = api_client.BaseApiClient._ensure_aiohttp_ssl_ctx(
        options
    )
    assert async_client_args["ssl"]
    assert isinstance(async_client_args["ssl"], ssl.SSLContext)
  except ImportError:
    assert async_client_args["verify"]
    assert isinstance(async_client_args["verify"], ssl.SSLContext)


def test_client_ssl_context_explicit_initialization_separate_args():
  ctx = ssl.create_default_context(
      cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
      capath=os.environ.get("SSL_CERT_DIR"),
  )

  async_ctx = ssl.create_default_context(
      cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
      capath=os.environ.get("SSL_CERT_DIR"),
  )

  options = types.HttpOptions(
      client_args={"verify": ctx}, async_client_args={"verify": async_ctx}
  )
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(options)
  )

  assert client_args["verify"] == ctx
  try:
    import aiohttp  # pylint: disable=g-import-not-at-top

    async_client_args = api_client.BaseApiClient._ensure_aiohttp_ssl_ctx(
        options
    )
    assert async_client_args["ssl"]
    assert isinstance(async_client_args["ssl"], ssl.SSLContext)
  except ImportError:
    assert async_client_args["verify"]
    assert isinstance(async_client_args["verify"], ssl.SSLContext)


def test_client_ssl_context_explicit_initialization_sync_args():
  ctx = ssl.create_default_context(
      cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
      capath=os.environ.get("SSL_CERT_DIR"),
  )

  options = types.HttpOptions(client_args={"verify": ctx})
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(options)
  )

  assert client_args["verify"] == ctx
  try:
    import aiohttp  # pylint: disable=g-import-not-at-top

    async_client_args = api_client.BaseApiClient._ensure_aiohttp_ssl_ctx(
        options
    )
    assert async_client_args["ssl"]
    assert isinstance(async_client_args["ssl"], ssl.SSLContext)
  except ImportError:
    assert async_client_args["verify"]
    assert isinstance(async_client_args["verify"], ssl.SSLContext)


def test_client_ssl_context_explicit_initialization_async_args():
  ctx = ssl.create_default_context(
      cafile=os.environ.get("SSL_CERT_FILE", certifi.where()),
      capath=os.environ.get("SSL_CERT_DIR"),
  )

  options = types.HttpOptions(async_client_args={"verify": ctx})
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(options)
  )

  assert client_args["verify"] == ctx
  try:
    import aiohttp  # pylint: disable=g-import-not-at-top

    async_client_args = api_client.BaseApiClient._ensure_aiohttp_ssl_ctx(
        options
    )
    assert async_client_args["ssl"]
    assert isinstance(async_client_args["ssl"], ssl.SSLContext)
  except ImportError:
    assert async_client_args["verify"]
    assert isinstance(async_client_args["verify"], ssl.SSLContext)


def test_constructor_with_base_url_from_http_options():
  mldev_http_options = {
      "base_url": "https://placeholder-fake-url.com/",
  }
  vertexai_http_options = {
      "base_url": (
          "https://{self.location}-aiplatform.googleapis.com/{{api_version}}/"
      ),
  }

  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://placeholder-fake-url.com/"
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


def test_constructor_with_base_url_from_set_default_base_urls():
  base_url.set_default_base_urls(
      gemini_url="https://gemini-base-url.com/",
      vertex_url="https://vertex-base-url.com/",
  )
  mldev_client = Client(api_key="google_api_key")
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://gemini-base-url.com/"
  )

  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
  )
  assert vertexai_client.models._api_client.vertexai
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "base_url"
      ]
      == "https://vertex-base-url.com/"
  )
  base_url.set_default_base_urls(gemini_url=None, vertex_url=None)


def test_constructor_with_constructor_base_url_overrides_set_default_base_urls():
  mldev_http_options = {
      "base_url": "https://gemini-constructor-base-url.com/",
  }
  vertexai_http_options = {
      "base_url": "https://vertex-constructor-base-url.com/",
  }

  base_url.set_default_base_urls(
      gemini_url="https://gemini-base-url.com/",
      vertex_url="https://vertex-base-url.com/",
  )
  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://gemini-constructor-base-url.com/"
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
      == "https://vertex-constructor-base-url.com/"
  )
  base_url.set_default_base_urls(gemini_url=None, vertex_url=None)


def test_constructor_with_constructor_base_url_overrides_environment_variables(
    monkeypatch,
):
  monkeypatch.setenv(
      "GOOGLE_GEMINI_BASE_URL", "https://gemini-env-base-url.com/"
  )
  monkeypatch.setenv(
      "GOOGLE_VERTEX_BASE_URL", "https://vertex-env-base-url.com/"
  )

  mldev_http_options = {
      "base_url": "https://gemini-constructor-base-url.com/",
  }
  vertexai_http_options = {
      "base_url": "https://vertex-constructor-base-url.com/",
  }

  mldev_client = Client(
      api_key="google_api_key", http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://gemini-constructor-base-url.com/"
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
      == "https://vertex-constructor-base-url.com/"
  )
  base_url.set_default_base_urls(gemini_url=None, vertex_url=None)


def test_constructor_with_base_url_from_set_default_base_urls_overrides_environment_variables(
    monkeypatch,
):
  monkeypatch.setenv(
      "GOOGLE_GEMINI_BASE_URL", "https://gemini-env-base-url.com/"
  )
  monkeypatch.setenv(
      "GOOGLE_VERTEX_BASE_URL", "https://vertex-env-base-url.com/"
  )

  base_url.set_default_base_urls(
      gemini_url="https://gemini-base-url.com/",
      vertex_url="https://vertex-base-url.com/",
  )
  mldev_client = Client(api_key="google_api_key")
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://gemini-base-url.com/"
  )

  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
  )
  assert vertexai_client.models._api_client.vertexai
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "base_url"
      ]
      == "https://vertex-base-url.com/"
  )
  base_url.set_default_base_urls(gemini_url=None, vertex_url=None)


def test_constructor_with_base_url_from_environment_variables(monkeypatch):
  monkeypatch.setenv("GOOGLE_GEMINI_BASE_URL", "https://gemini-base-url.com/")
  monkeypatch.setenv("GOOGLE_VERTEX_BASE_URL", "https://vertex-base-url.com/")

  mldev_client = Client(api_key="google_api_key")
  assert not mldev_client.models._api_client.vertexai
  assert (
      mldev_client.models._api_client.get_read_only_http_options()["base_url"]
      == "https://gemini-base-url.com/"
  )

  vertexai_client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
  )
  assert vertexai_client.models._api_client.vertexai
  assert (
      vertexai_client.models._api_client.get_read_only_http_options()[
          "base_url"
      ]
      == "https://vertex-base-url.com/"
  )


def test_async_transport_absence_allows_aiohttp_to_be_used():
  client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
  )

  api_client.has_aiohttp = False
  assert not client._api_client._use_aiohttp()

  api_client.has_aiohttp = True
  assert client._api_client._use_aiohttp()


def test_async_async_client_args_without_transport_allows_aiohttp_to_be_used():
  client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
      http_options=types.HttpOptions(async_client_args={}),
  )

  api_client.has_aiohttp = False
  assert not client._api_client._use_aiohttp()

  api_client.has_aiohttp = True
  assert client._api_client._use_aiohttp()


def test_async_transport_forces_httpx_regardless_of_aiohttp_availability():

  client = Client(
      vertexai=True,
      project="fake_project_id",
      location="fake-location",
      http_options=types.HttpOptions(
          async_client_args={"transport": httpx.AsyncBaseTransport()}
      ),
  )

  api_client.has_aiohttp = False
  assert not client._api_client._use_aiohttp()

  api_client.has_aiohttp = True
  assert not client._api_client._use_aiohttp()


@pytest.mark.asyncio
async def test_get_async_auth_lock_basic_functionality():
  """Tests that _get_async_auth_lock returns an asyncio.Lock."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  lock = await client._api_client._get_async_auth_lock()
  assert isinstance(lock, asyncio.Lock)
  assert client._api_client._async_auth_lock is lock


@pytest.mark.asyncio
async def test_get_async_auth_lock_returns_same_instance():
  """Tests that multiple calls return the same lock instance."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )
  lock1 = await client._api_client._get_async_auth_lock()
  lock2 = await client._api_client._get_async_auth_lock()
  lock3 = await client._api_client._get_async_auth_lock()
  assert lock1 is lock2
  assert lock2 is lock3
  assert isinstance(lock1, asyncio.Lock)


def test_threaded_generate_content_locking(monkeypatch):
  """Tests that synchronous API calls are thread-safe."""
  monkeypatch.delenv("GOOGLE_GENAI_CLIENT_MODE", raising=False)
  # Mock credentials
  mock_creds = mock.Mock(spec=credentials.Credentials)
  mock_creds.token = "initial-token"
  mock_creds.expired = False
  mock_creds.quota_project_id = None

  # Mock google.auth.default
  mock_auth_default = mock.Mock(return_value=(mock_creds, "test-project"))
  monkeypatch.setattr(google.auth, "default", mock_auth_default)

  # Mock Credentials.refresh
  def refresh_side_effect(request):
    mock_creds.token = "refreshed-token"
    mock_creds.expired = False

  mock_refresh = mock.Mock(side_effect=refresh_side_effect)
  mock_creds.refresh = mock_refresh

  # Mock the actual request to avoid network calls
  mock_httpx_response = httpx.Response(
      status_code=200,
      headers={},
      text='{"candidates": [{"content": {"parts": [{"text": "response"}]}}]}',
  )
  mock_request = mock.Mock(return_value=mock_httpx_response)
  monkeypatch.setattr(api_client.SyncHttpxClient, "request", mock_request)

  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )
  # Reset credentials to test initialization to ensure the sync lock is tested.
  client._api_client._credentials = None

  # 1. Test initial credential loading in multiple threads
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(
            client.models.generate_content, model="gemini-pro", contents=str(i)
        )
        for i in range(10)
    ]
    for future in concurrent.futures.as_completed(futures):
      assert future.result().text == "response"

  mock_auth_default.assert_called_once()
  mock_refresh.assert_not_called()
  assert mock_request.call_count == 10

  # 2. Test credential refreshing in multiple threads
  mock_creds.expired = True
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(
            client.models.generate_content, model="gemini-pro", contents=str(i)
        )
        for i in range(10)
    ]
    for future in concurrent.futures.as_completed(futures):
      assert future.result().text == "response"

  mock_auth_default.assert_called_once()
  mock_refresh.assert_called_once()
  assert mock_request.call_count == 20


@pytest.mark.asyncio
async def test_async_access_token_locking(monkeypatch):
  """Tests that _async_access_token uses locks to prevent race conditions."""
  # Mock credentials
  mock_creds = mock.Mock(spec=credentials.Credentials)
  mock_creds.token = "initial-token"
  mock_creds.expired = False
  mock_creds.quota_project_id = None

  # Mock google.auth.default
  mock_auth_default = mock.Mock(return_value=(mock_creds, "test-project"))
  monkeypatch.setattr(google.auth, "default", mock_auth_default)

  # Mock Credentials.refresh
  def refresh_side_effect(request):
    mock_creds.token = "refreshed-token"
    mock_creds.expired = False

  mock_refresh = mock.Mock(side_effect=refresh_side_effect)
  mock_creds.refresh = mock_refresh

  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )
  # Reset credentials to test initialization to ensure the async lock is tested.
  client._api_client._credentials = None

  # 1. Test initial credential loading
  # Running them concurrently should result in only one call to load_auth.
  tokens = await asyncio.gather(
      client._api_client._async_access_token(),
      client._api_client._async_access_token(),
      client._api_client._async_access_token(),
  )

  assert tokens == ["initial-token", "initial-token", "initial-token"]
  mock_auth_default.assert_called_once()
  mock_refresh.assert_not_called()

  # 2. Test credential refreshing
  # Now the token is "expired", so the next call should refresh it.
  mock_creds.expired = True

  # Running them concurrently should result in only one call to refresh.
  tokens = await asyncio.gather(
      client._api_client._async_access_token(),
      client._api_client._async_access_token(),
      client._api_client._async_access_token(),
  )

  assert tokens == ["refreshed-token", "refreshed-token", "refreshed-token"]
  # google.auth.default should still have been called only once in total.
  mock_auth_default.assert_called_once()
  mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_async_auth_lock_concurrent_access():
  """Tests that concurrent access to _get_async_auth_lock is thread-safe."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  # Run multiple concurrent calls
  async def get_lock_task(task_id: int):
    lock = await client._api_client._get_async_auth_lock()
    return task_id, id(lock)

  tasks = [get_lock_task(i) for i in range(20)]
  results = await asyncio.gather(*tasks)

  # All tasks should get the same lock instance
  lock_ids = [result[1] for result in results]
  assert all(
      lock_id == lock_ids[0] for lock_id in lock_ids
  ), "All tasks should get the same lock instance"

  # All tasks should complete
  task_ids = [result[0] for result in results]
  assert sorted(task_ids) == list(range(20)), "All tasks should complete"


@pytest.mark.asyncio
async def test_get_async_auth_lock_doesnt_block_other_operations():
  """Tests that _get_async_auth_lock doesn't interfere with other async operations."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  # Track completion of other async operations
  completed_operations = []

  async def mock_async_operation(op_id: int):
    await asyncio.sleep(0.01)  # Small delay to simulate async work
    completed_operations.append(op_id)
    return f"operation_{op_id}"

  # Start auth lock requests and other operations simultaneously
  start_time = asyncio.get_event_loop().time()

  auth_tasks = [client._api_client._get_async_auth_lock() for _ in range(10)]
  work_tasks = [mock_async_operation(i) for i in range(15)]

  auth_results, work_results = await asyncio.gather(
      asyncio.gather(*auth_tasks), asyncio.gather(*work_tasks)
  )

  end_time = asyncio.get_event_loop().time()
  total_time = end_time - start_time

  # Verify all operations completed
  assert len(auth_results) == 10, "All auth lock requests should complete"
  assert len(work_results) == 15, "All work tasks should complete"
  assert len(completed_operations) == 15, "All async operations should complete"

  # All auth requests should return the same lock
  lock_ids = [id(lock) for lock in auth_results]
  assert all(lock_id == lock_ids[0] for lock_id in lock_ids)

  # Should complete quickly since operations run concurrently
  assert total_time < 0.1, (
      f"Operations took too long ({total_time:.3f}s), suggesting blocking"
      " occurred"
  )


@pytest.mark.asyncio
async def test_get_async_auth_lock_creation_lock_lifecycle():
  """Tests the creation lock lifecycle and cleanup."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  # Initially, both locks should be None
  assert client._api_client._async_auth_lock is None
  assert client._api_client._async_auth_lock_creation_lock is None

  # After first call, both should exist
  lock1 = await client._api_client._get_async_auth_lock()
  assert client._api_client._async_auth_lock is not None
  assert client._api_client._async_auth_lock_creation_lock is not None
  assert isinstance(lock1, asyncio.Lock)

  # Creation lock should be different from the auth lock
  creation_lock = client._api_client._async_auth_lock_creation_lock
  assert creation_lock is not lock1
  assert isinstance(creation_lock, asyncio.Lock)

  # Subsequent calls should reuse both locks
  lock2 = await client._api_client._get_async_auth_lock()
  assert lock2 is lock1
  assert client._api_client._async_auth_lock_creation_lock is creation_lock


@pytest.mark.asyncio
async def test_get_async_auth_lock_under_load():
  """Tests _get_async_auth_lock under heavy concurrent load."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  num_concurrent_calls = 100

  async def get_lock_with_timing(call_id: int):
    start = asyncio.get_event_loop().time()
    lock = await client._api_client._get_async_auth_lock()
    end = asyncio.get_event_loop().time()
    return call_id, id(lock), end - start

  # Run many concurrent calls
  start_time = asyncio.get_event_loop().time()
  tasks = [get_lock_with_timing(i) for i in range(num_concurrent_calls)]
  results = await asyncio.gather(*tasks)
  total_time = asyncio.get_event_loop().time() - start_time

  # Verify all calls succeeded and got the same lock
  call_ids = [r[0] for r in results]
  lock_ids = [r[1] for r in results]
  call_times = [r[2] for r in results]

  assert len(results) == num_concurrent_calls
  assert sorted(call_ids) == list(range(num_concurrent_calls))
  assert all(
      lock_id == lock_ids[0] for lock_id in lock_ids
  ), "All calls should get same lock"

  # Performance checks
  max_call_time = max(call_times)
  assert total_time < 1.0, f"Total time ({total_time:.3f}s) suggests blocking"
  assert (
      max_call_time < 0.1
  ), f"Max individual call time ({max_call_time:.3f}s) too high"


@pytest.mark.asyncio
async def test_get_async_auth_lock_interleaved_with_auth_operations():
  """Tests _get_async_auth_lock working correctly with actual auth operations."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  # Mock credentials for this test
  mock_creds = mock.Mock(spec=credentials.Credentials)
  mock_creds.token = "test-token"
  mock_creds.expired = False
  mock_creds.quota_project_id = None
  client._api_client._credentials = mock_creds

  # Mix lock requests with simulated auth operations
  async def auth_operation(op_id: int):
    # This simulates what _async_access_token does
    lock = await client._api_client._get_async_auth_lock()
    async with lock:
      await asyncio.sleep(0.001)  # Simulate auth work
      return f"auth_op_{op_id}"

  async def lock_request(req_id: int):
    lock = await client._api_client._get_async_auth_lock()
    return req_id, id(lock)

  # Interleave different types of operations
  auth_tasks = [auth_operation(i) for i in range(10)]
  lock_tasks = [lock_request(i) for i in range(10)]

  auth_results, lock_results = await asyncio.gather(
      asyncio.gather(*auth_tasks), asyncio.gather(*lock_tasks)
  )

  # Verify all operations completed
  assert len(auth_results) == 10
  assert len(lock_results) == 10

  # All lock requests should return the same lock ID
  lock_ids = [result[1] for result in lock_results]
  assert all(lock_id == lock_ids[0] for lock_id in lock_ids)

  # Auth operations should complete successfully
  assert all(result.startswith("auth_op_") for result in auth_results)


@pytest.mark.asyncio
async def test_get_async_auth_lock_with_event_loop_switch():
  """Tests that _get_async_auth_lock works correctly with event loop context."""

  async def create_client_and_get_lock():
    client = Client(
        vertexai=True, project="fake_project_id", location="fake-location"
    )
    lock = await client._api_client._get_async_auth_lock()
    return client, lock

  # Create client and get lock in current event loop
  client, lock1 = await create_client_and_get_lock()

  # Get lock again in same event loop
  lock2 = await client._api_client._get_async_auth_lock()

  assert lock1 is lock2
  assert isinstance(lock1, asyncio.Lock)

  # Verify the locks work correctly
  async def test_lock_functionality():
    async with lock1:
      await asyncio.sleep(0.001)
      return "success"

  result = await test_lock_functionality()
  assert result == "success"


@pytest.mark.asyncio
async def test_get_async_auth_lock_double_checked_locking():
  """Tests the double-checked locking pattern implementation."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )

  original_lock_init = asyncio.Lock.__init__
  lock_creation_count = [0]

  def counting_lock_init(self):
    lock_creation_count[0] += 1
    return original_lock_init(self)

  # Patch asyncio.Lock to count creations
  asyncio.Lock.__init__ = counting_lock_init

  try:
    # Run many concurrent requests
    tasks = [client._api_client._get_async_auth_lock() for _ in range(50)]
    locks = await asyncio.gather(*tasks)

    # All should be the same instance
    assert all(lock is locks[0] for lock in locks)

    # Should only create 2 locks: creation_lock + auth_lock
    # (Could be slightly more due to asyncio internals, but should be minimal)
    assert (
        lock_creation_count[0] <= 5
    ), f"Created {lock_creation_count[0]} locks, expected ~2"

  finally:
    asyncio.Lock.__init__ = original_lock_init


@pytest.mark.asyncio
async def test_get_async_auth_lock_memory_efficiency():
  """Tests that _get_async_auth_lock doesn't leak memory under repeated use."""
  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )
  initial_lock = await client._api_client._get_async_auth_lock()
  initial_creation_lock = client._api_client._async_auth_lock_creation_lock

  # Run many operations
  for _ in range(100):
    lock = await client._api_client._get_async_auth_lock()
    assert lock is initial_lock
    assert (
        client._api_client._async_auth_lock_creation_lock
        is initial_creation_lock
    )
  # Verify no new objects were created
  final_lock = await client._api_client._get_async_auth_lock()
  final_creation_lock = client._api_client._async_auth_lock_creation_lock

  assert final_lock is initial_lock
  assert final_creation_lock is initial_creation_lock


@requires_aiohttp
@pytest.mark.asyncio
async def test_get_aiohttp_session():
  """Tests that _get_async_auth_lock works correctly with aiohttp session lock."""

  client = Client(
      vertexai=True, project="fake_project_id", location="fake-location"
  )
  api_client.has_aiohttp = True
  initial_session = await client._api_client._get_aiohttp_session()
  assert initial_session is not None
  session = await client._api_client._get_aiohttp_session()
  assert session is initial_session
