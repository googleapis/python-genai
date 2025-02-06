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

import os
from typing import Optional, Union

import google.auth
import pydantic

from ._api_client import ApiClient, HttpOptions, HttpOptionsDict
from ._replay_api_client import ReplayApiClient
from .batches import AsyncBatches, Batches
from .caches import AsyncCaches, Caches
from .chats import AsyncChats, Chats
from .files import AsyncFiles, Files
from .live import AsyncLive
from .models import AsyncModels, Models
from .tunings import AsyncTunings, Tunings


class AsyncClient:
  """Client for making asynchronous (non-blocking) requests."""

  def __init__(self, api_client: ApiClient):

    self._api_client = api_client
    self._models = AsyncModels(self._api_client)
    self._tunings = AsyncTunings(self._api_client)
    self._caches = AsyncCaches(self._api_client)
    self._batches = AsyncBatches(self._api_client)
    self._files = AsyncFiles(self._api_client)
    self._live = AsyncLive(self._api_client)

  @property
  def models(self) -> AsyncModels:
    return self._models

  @property
  def tunings(self) -> AsyncTunings:
    return self._tunings

  @property
  def caches(self) -> AsyncCaches:
    return self._caches

  @property
  def batches(self) -> AsyncBatches:
    return self._batches

  @property
  def chats(self) -> AsyncChats:
    return AsyncChats(modules=self.models)

  @property
  def files(self) -> AsyncFiles:
    return self._files

  @property
  def live(self) -> AsyncLive:
    return self._live


class DebugConfig(pydantic.BaseModel):
  """Configuration options that change client network behavior when testing."""

  client_mode: Optional[str] = pydantic.Field(
      default_factory=lambda: os.getenv('GOOGLE_GENAI_CLIENT_MODE', None)
  )

  replays_directory: Optional[str] = pydantic.Field(
      default_factory=lambda: os.getenv('GOOGLE_GENAI_REPLAYS_DIRECTORY', None)
  )

  replay_id: Optional[str] = pydantic.Field(
      default_factory=lambda: os.getenv('GOOGLE_GENAI_REPLAY_ID', None)
  )


class Client:
  """Client for making synchronous requests.

  Use this client to make a request to the Gemini Developer API or Vertex AI
  API and then wait for the response.

  Attributes:
    api_key: The `API key <https://ai.google.dev/gemini-api/docs/api-key>`_ to
      use for authentication. Applies to the Gemini Developer API only.
    vertexai: Indicates whether the client should use the Vertex AI
      API endpoints. Defaults to False (uses Gemini Developer API endpoints).
      Applies to the Vertex AI API only.
    credentials: The credentials to use for authentication when calling the
      Vertex AI APIs. Credentials can be obtained from environment variables and
      default credentials. For more information, see
      `Set up Application Default Credentials
      <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
      Applies to the Vertex AI API only.
    project: The `Google Cloud project ID <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
      use for quota. Can be obtained from environment variables (for example,
      ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
    location: The `location <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
      to send API requests to (for example, ``us-central1``). Can be obtained
      from environment variables. Applies to the Vertex AI API only.
    debug_config: Config settings that control network behavior of the client.
      This is typically used when running test code.
    http_options: Http options to use for the client. Response_payload can't be
      set when passing to the client constructor.

  Usage for the Gemini Developer API:

  .. code-block:: python

    from google import genai

    client = genai.Client(api_key='my-api-key')

  Usage for the Vertex AI API:

  .. code-block:: python

    from google import genai

    client = genai.Client(
        vertexai=True, project='my-project-id', location='us-central1'
    )
  """

  def __init__(
      self,
      *,
      vertexai: Optional[bool] = None,
      api_key: Optional[str] = None,
      credentials: Optional[google.auth.credentials.Credentials] = None,
      project: Optional[str] = None,
      location: Optional[str] = None,
      debug_config: Optional[DebugConfig] = None,
      http_options: Optional[Union[HttpOptions, HttpOptionsDict]] = None,
  ):
    """Initializes the client.

    Args:
       vertexai (bool): Indicates whether the client should use the Vertex AI
         API endpoints. Defaults to False (uses Gemini Developer API endpoints).
         Applies to the Vertex AI API only.
       api_key (str): The `API key
         <https://ai.google.dev/gemini-api/docs/api-key>`_ to use for
         authentication. Applies to the Gemini Developer API only.
       credentials (google.auth.credentials.Credentials): The credentials to use
         for authentication when calling the Vertex AI APIs. Credentials can be
         obtained from environment variables and default credentials. For more
         information, see `Set up Application Default Credentials
         <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
         Applies to the Vertex AI API only.
       project (str): The `Google Cloud project ID
         <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
         use for quota. Can be obtained from environment variables (for example,
         ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
       location (str): The `location
         <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
         to send API requests to (for example, ``us-central1``). Can be obtained
         from environment variables. Applies to the Vertex AI API only.
       debug_config (DebugConfig): Config settings that control network behavior
         of the client. This is typically used when running test code.
       http_options (Union[HttpOptions, HttpOptionsDict]): Http options to use
         for the client. The field deprecated_response_payload should not be set
         in http_options.
    """

    self._debug_config = debug_config or DebugConfig()

    # Throw ValueError if deprecated_response_payload is set in http_options
    # due to unpredictable behavior when running multiple coroutines through
    # client.aio.
    if http_options and 'deprecated_response_payload' in http_options:
      raise ValueError(
          'Setting deprecated_response_payload in http_options is not'
          ' supported.'
      )

    self._api_client = self._get_api_client(
        vertexai=vertexai,
        api_key=api_key,
        credentials=credentials,
        project=project,
        location=location,
        debug_config=self._debug_config,
        http_options=http_options,
    )

    self._aio = AsyncClient(self._api_client)
    self._models = Models(self._api_client)
    self._tunings = Tunings(self._api_client)
    self._caches = Caches(self._api_client)
    self._batches = Batches(self._api_client)
    self._files = Files(self._api_client)

  @staticmethod
  def _get_api_client(
      vertexai: Optional[bool] = None,
      api_key: Optional[str] = None,
      credentials: Optional[google.auth.credentials.Credentials] = None,
      project: Optional[str] = None,
      location: Optional[str] = None,
      debug_config: Optional[DebugConfig] = None,
      http_options: Optional[HttpOptions] = None,
  ):
    if debug_config and debug_config.client_mode in [
        'record',
        'replay',
        'auto',
    ]:
      return ReplayApiClient(
          mode=debug_config.client_mode,
          replay_id=debug_config.replay_id,
          replays_directory=debug_config.replays_directory,
          vertexai=vertexai,
          api_key=api_key,
          credentials=credentials,
          project=project,
          location=location,
          http_options=http_options,
      )

    return ApiClient(
        vertexai=vertexai,
        api_key=api_key,
        credentials=credentials,
        project=project,
        location=location,
        http_options=http_options,
    )

  @property
  def chats(self) -> Chats:
    return Chats(modules=self.models)

  @property
  def aio(self) -> AsyncClient:
    return self._aio

  @property
  def models(self) -> Models:
    return self._models

  @property
  def tunings(self) -> Tunings:
    return self._tunings

  @property
  def caches(self) -> Caches:
    return self._caches

  @property
  def batches(self) -> Batches:
    return self._batches

  @property
  def files(self) -> Files:
    return self._files

  @property
  def vertexai(self) -> bool:
    """Returns whether the client is using the Vertex AI API."""
    return self._api_client.vertexai or False
