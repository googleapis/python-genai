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


"""Base client for calling HTTP APIs sending and receiving JSON."""

import asyncio
import copy
from dataclasses import dataclass
import datetime
import io
import json
import logging
import os
import sys
from typing import Any, Optional, Tuple, TypedDict, Union
from urllib.parse import urlparse, urlunparse

import google.auth
import google.auth.credentials
from google.auth.transport.requests import AuthorizedSession
from pydantic import BaseModel, ConfigDict, Field, ValidationError
import requests

from . import errors
from . import version
from .types import HttpOptions, HttpOptionsDict, HttpOptionsOrDict


def _append_library_version_headers(headers: dict[str, str]) -> None:
  """Appends the telemetry header to the headers dict."""
  library_label = f'google-genai-sdk/{version.__version__}'
  language_label = 'gl-python/' + sys.version.split()[0]
  version_header_value = f'{library_label} {language_label}'
  if (
      'user-agent' in headers
      and version_header_value not in headers['user-agent']
  ):
    headers['user-agent'] += f' {version_header_value}'
  elif 'user-agent' not in headers:
    headers['user-agent'] = version_header_value
  if (
      'x-goog-api-client' in headers
      and version_header_value not in headers['x-goog-api-client']
  ):
    headers['x-goog-api-client'] += f' {version_header_value}'
  elif 'x-goog-api-client' not in headers:
    headers['x-goog-api-client'] = version_header_value


def _patch_http_options(
    options: HttpOptionsDict, patch_options: HttpOptionsDict
) -> HttpOptionsDict:
  # use shallow copy so we don't override the original objects.
  copy_option = HttpOptionsDict()
  copy_option.update(options)
  for patch_key, patch_value in patch_options.items():
    # if both are dicts, update the copy.
    # This is to handle cases like merging headers.
    if isinstance(patch_value, dict) and isinstance(
        copy_option.get(patch_key, None), dict
    ):
      copy_option[patch_key] = {}
      copy_option[patch_key].update(
          options[patch_key]
      )  # shallow copy from original options.
      copy_option[patch_key].update(patch_value)
    elif patch_value is not None:  # Accept empty values.
      copy_option[patch_key] = patch_value
  _append_library_version_headers(copy_option['headers'])
  return copy_option


def _join_url_path(base_url: str, path: str) -> str:
  parsed_base = urlparse(base_url)
  base_path = parsed_base.path[:-1] if parsed_base.path.endswith('/') else parsed_base.path
  path = path[1:] if path.startswith('/') else path
  return urlunparse(parsed_base._replace(path=base_path + '/' + path))


@dataclass
class HttpRequest:
  headers: dict[str, str]
  url: str
  method: str
  data: Union[dict[str, object], bytes]
  timeout: Optional[float] = None


# TODO(b/394358912): Update this class to use a SDKResponse class that can be
# generated and used for all languages.
@dataclass
class BaseResponse:
  http_headers: dict[str, str]

  @property
  def dict(self) -> dict[str, Any]:
    if isinstance(self, dict):
      return self
    return {'httpHeaders': self.http_headers}


class HttpResponse:

  def __init__(
      self,
      headers: dict[str, str],
      response_stream: Union[Any, str] = None,
      byte_stream: Union[Any, bytes] = None,
  ):
    self.status_code = 200
    self.headers = headers
    self.response_stream = response_stream
    self.byte_stream = byte_stream
    self.segment_iterator = self.segments()

  # Async iterator for async streaming.
  def __aiter__(self):
    return self

  async def __anext__(self):
    try:
      return next(self.segment_iterator)
    except StopIteration:
      raise StopAsyncIteration

  @property
  def json(self) -> Any:
    if not self.response_stream[0]:  # Empty response
      return ''
    return json.loads(self.response_stream[0])

  def segments(self):
    if isinstance(self.response_stream, list):
      # list of objects retrieved from replay or from non-streaming API.
      for chunk in self.response_stream:
        yield json.loads(chunk) if chunk else {}
    elif self.response_stream is None:
      yield from []
    else:
      # Iterator of objects retrieved from the API.
      for chunk in self.response_stream.iter_lines():
        if chunk:
          # In streaming mode, the chunk of JSON is prefixed with "data:" which
          # we must strip before parsing.
          if chunk.startswith(b'data: '):
            chunk = chunk[len(b'data: ') :]
          yield json.loads(str(chunk, 'utf-8'))

  def byte_segments(self):
    if isinstance(self.byte_stream, list):
      # list of objects retrieved from replay or from non-streaming API.
      yield from self.byte_stream
    elif self.byte_stream is None:
      yield from []
    else:
      raise ValueError(
          'Byte segments are not supported for streaming responses.'
      )

  def _copy_to_dict(self, response_payload: dict[str, object]):
    # Cannot pickle 'generator' object.
    delattr(self, 'segment_iterator')
    for attribute in dir(self):
      response_payload[attribute] = copy.deepcopy(getattr(self, attribute))


class ApiClient:
  """Client for calling HTTP APIs sending and receiving JSON."""

  def __init__(
      self,
      vertexai: Union[bool, None] = None,
      api_key: Union[str, None] = None,
      credentials: google.auth.credentials.Credentials = None,
      project: Union[str, None] = None,
      location: Union[str, None] = None,
      http_options: HttpOptionsOrDict = None,
  ):
    self.vertexai = vertexai
    if self.vertexai is None:
      if os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', '0').lower() in [
          'true',
          '1',
      ]:
        self.vertexai = True

    # Validate explicitly set initializer values.
    if (project or location) and api_key:
      # API cannot consume both project/location and api_key.
      raise ValueError(
          'Project/location and API key are mutually exclusive in the client initializer.'
      )
    elif credentials and api_key:
      # API cannot consume both credentials and api_key.
      raise ValueError(
          'Credentials and API key are mutually exclusive in the client initializer.'
      )

    # Validate http_options if a dict is provided.
    if isinstance(http_options, dict):
      try:
        HttpOptions.model_validate(http_options)
      except ValidationError as e:
        raise ValueError(f'Invalid http_options: {e}')
    elif(isinstance(http_options, HttpOptions)):
      http_options = http_options.model_dump()

    # Retrieve implicitly set values from the environment.
    env_project = os.environ.get('GOOGLE_CLOUD_PROJECT', None)
    env_location = os.environ.get('GOOGLE_CLOUD_LOCATION', None)
    env_api_key = os.environ.get('GOOGLE_API_KEY', None)
    self.project = project or env_project
    self.location = location or env_location
    self.api_key = api_key or env_api_key

    self._credentials = credentials
    self._http_options = HttpOptionsDict()

    # Handle when to use Vertex AI in express mode (api key).
    # Explicit initializer arguments are already validated above.
    if self.vertexai:
      if credentials:
        # Explicit credentials take precedence over implicit api_key.
        logging.info(
            'The user provided Google Cloud credentials will take precedence'
            + ' over the API key from the environment variable.'
        )
        self.api_key = None
      elif (env_location or env_project) and api_key:
        # Explicit api_key takes precedence over implicit project/location.
        logging.info(
            'The user provided Vertex AI API key will take precedence over the'
            + ' project/location from the environment variables.'
        )
        self.project = None
        self.location = None
      elif (project or location) and env_api_key:
        # Explicit project/location takes precedence over implicit api_key.
        logging.info(
            'The user provided project/location will take precedence over the'
            + ' Vertex AI API key from the environment variable.'
        )
        self.api_key = None
      elif (env_location or env_project) and env_api_key:
        # Implicit project/location takes precedence over implicit api_key.
        logging.info(
            'The project/location from the environment variables will take'
            + ' precedence over the API key from the environment variables.'
        )
        self.api_key = None
      if not self.project and not self.api_key:
        self.project = google.auth.default()[1]
      if not ((self.project and self.location) or self.api_key):
        raise ValueError(
            'Project and location or API key must be set when using the Vertex '
            'AI API.'
        )
      if self.api_key or self.location == 'global':
        self._http_options['base_url'] = (
            f'https://aiplatform.googleapis.com/'
        )
      else:
        self._http_options['base_url'] = (
            f'https://{self.location}-aiplatform.googleapis.com/'
        )
      self._http_options['api_version'] = 'v1beta1'
    else:  # ML Dev API
      if not self.api_key:
        raise ValueError('API key must be set when using the Google AI API.')
      self._http_options['base_url'] = (
          'https://generativelanguage.googleapis.com/'
      )
      self._http_options['api_version'] = 'v1beta'
    # Default options for both clients.
    self._http_options['headers'] = {'Content-Type': 'application/json'}
    if self.api_key:
      self._http_options['headers']['x-goog-api-key'] = self.api_key
    # Update the http options with the user provided http options.
    if http_options:
      self._http_options = _patch_http_options(self._http_options, http_options)
    else:
      _append_library_version_headers(self._http_options['headers'])

  def _websocket_base_url(self):
    url_parts = urlparse(self._http_options['base_url'])
    return url_parts._replace(scheme='wss').geturl()

  def _build_request(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptionsOrDict = None,
  ) -> HttpRequest:
    # Remove all special dict keys such as _url and _query.
    keys_to_delete = [key for key in request_dict.keys() if key.startswith('_')]
    for key in keys_to_delete:
      del request_dict[key]
    # patch the http options with the user provided settings.
    if http_options:
      if isinstance(http_options, HttpOptions):
        patched_http_options = _patch_http_options(
            self._http_options, http_options.model_dump()
        )
      else:
        patched_http_options = _patch_http_options(
            self._http_options, http_options
        )
    else:
      patched_http_options = self._http_options
    # Skip adding project and locations when getting Vertex AI base models.
    query_vertex_base_models = False
    if (
        self.vertexai
        and http_method == 'get'
        and path.startswith('publishers/google/models')
    ):
      query_vertex_base_models = True
    if (
        self.vertexai
        and not path.startswith('projects/')
        and not query_vertex_base_models
        and not self.api_key
    ):
      path = f'projects/{self.project}/locations/{self.location}/' + path
    url = _join_url_path(
        patched_http_options['base_url'],
        patched_http_options['api_version'] + '/' + path,
    )

    timeout_in_seconds = patched_http_options.get('timeout', None)
    if timeout_in_seconds:
      timeout_in_seconds = timeout_in_seconds / 1000.0
    else:
      timeout_in_seconds = None

    return HttpRequest(
        method=http_method,
        url=url,
        headers=patched_http_options['headers'],
        data=request_dict,
        timeout=timeout_in_seconds,
    )

  def _request(
      self,
      http_request: HttpRequest,
      stream: bool = False,
  ) -> HttpResponse:
    if self.vertexai and not self.api_key:
      if not self._credentials:
        self._credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
      authed_session = AuthorizedSession(self._credentials)
      authed_session.stream = stream
      response = authed_session.request(
          http_request.method.upper(),
          http_request.url,
          headers=http_request.headers,
          data=json.dumps(http_request.data)
          if http_request.data
          else None,
          timeout=http_request.timeout,
      )
      errors.APIError.raise_for_response(response)
      return HttpResponse(
          response.headers, response if stream else [response.text]
      )
    else:
      return self._request_unauthorized(http_request, stream)

  def _request_unauthorized(
      self,
      http_request: HttpRequest,
      stream: bool = False,
  ) -> HttpResponse:
    data = None
    if http_request.data:
      if not isinstance(http_request.data, bytes):
        data = json.dumps(http_request.data)
      else:
        data = http_request.data

    http_session = requests.Session()
    response = http_session.request(
        method=http_request.method,
        url=http_request.url,
        headers=http_request.headers,
        data=data,
        timeout=http_request.timeout,
        stream=stream,
    )
    errors.APIError.raise_for_response(response)
    return HttpResponse(
        response.headers, response if stream else [response.text]
    )

  async def _async_request(
      self, http_request: HttpRequest, stream: bool = False
  ):
    if self.vertexai:
      if not self._credentials:
        self._credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
      return await asyncio.to_thread(
          self._request,
          http_request,
          stream=stream,
      )
    else:
      return await asyncio.to_thread(
          self._request,
          http_request,
          stream=stream,
      )

  def get_read_only_http_options(self) -> HttpOptionsDict:
    copied = HttpOptionsDict()
    if isinstance(self._http_options, BaseModel):
      self._http_options = self._http_options.model_dump()
    copied.update(self._http_options)
    return copied

  def request(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptionsOrDict = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )
    response = self._request(http_request, stream=False)
    json_response = response.json
    if not json_response:
      base_response = BaseResponse(response.headers).dict
      return base_response

    return json_response

  def request_streamed(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptionsDict = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    session_response = self._request(http_request, stream=True)
    for chunk in session_response.segments():
      yield chunk

  async def async_request(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptionsDict = None,
  ) -> dict[str, object]:
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    result = await self._async_request(http_request=http_request, stream=False)
    json_response = result.json
    if not json_response:
      base_response = BaseResponse(result.headers).dict
      return base_response
    return json_response

  async def async_request_streamed(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptionsDict = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    response = await self._async_request(http_request=http_request, stream=True)

    async def async_generator():
      async for chunk in response:
        yield chunk
    return async_generator()

  def upload_file(
      self, file_path: Union[str, io.IOBase], upload_url: str, upload_size: int
  ) -> str:
    """Transfers a file to the given URL.

    Args:
      file_path: The full path to the file or a file like object inherited from
        io.BytesIO. If the local file path is not found, an error will be
        raised.
      upload_url: The URL to upload the file to.
      upload_size: The size of file content to be uploaded, this will have to
        match the size requested in the resumable upload request.

    returns:
          The response json object from the finalize request.
    """
    if isinstance(file_path, io.IOBase):
      return self._upload_fd(file_path, upload_url, upload_size)
    else:
      with open(file_path, 'rb') as file:
        return self._upload_fd(file, upload_url, upload_size)

  def _upload_fd(
      self, file: io.IOBase, upload_url: str, upload_size: int
  ) -> str:
    """Transfers a file to the given URL.

    Args:
      file: A file like object inherited from io.BytesIO.
      upload_url: The URL to upload the file to.
      upload_size: The size of file content to be uploaded, this will have to
        match the size requested in the resumable upload request.

    returns:
          The response json object from the finalize request.
    """
    offset = 0
    # Upload the file in chunks
    while True:
      file_chunk = file.read(1024 * 1024 * 8)  # 8 MB chunk size
      chunk_size = 0
      if file_chunk:
        chunk_size = len(file_chunk)
      upload_command = 'upload'
      # If last chunk, finalize the upload.
      if chunk_size + offset >= upload_size:
        upload_command += ', finalize'
      request = HttpRequest(
          method='POST',
          url=upload_url,
          headers={
              'X-Goog-Upload-Command': upload_command,
              'X-Goog-Upload-Offset': str(offset),
              'Content-Length': str(chunk_size),
          },
          data=file_chunk,
      )

      response = self._request_unauthorized(request, stream=False)
      offset += chunk_size
      if response.headers['X-Goog-Upload-Status'] != 'active':
        break  # upload is complete or it has been interrupted.

      if upload_size <= offset:  # Status is not finalized.
        raise ValueError(
            'All content has been uploaded, but the upload status is not'
            f' finalized. {response.headers}, body: {response.json}'
        )

    if response.headers['X-Goog-Upload-Status'] != 'final':
      raise ValueError(
          'Failed to upload file: Upload status is not finalized. headers:'
          f' {response.headers}, body: {response.json}'
      )
    return response.json

  def download_file(self, path: str, http_options):
    """Downloads the file data.

    Args:
      path: The request path with query params.
      http_options: The http options to use for the request.

    returns:
          The file bytes
    """
    http_request = self._build_request(
        'get', path=path, request_dict={}, http_options=http_options
    )
    return self._download_file_request(http_request).byte_stream[0]

  def _download_file_request(
      self,
      http_request: HttpRequest,
  ) -> HttpResponse:
    data = None
    if http_request.data:
      if not isinstance(http_request.data, bytes):
        data = json.dumps(http_request.data, cls=RequestJsonEncoder)
      else:
        data = http_request.data

    http_session = requests.Session()
    response = http_session.request(
        method=http_request.method,
        url=http_request.url,
        headers=http_request.headers,
        data=data,
        timeout=http_request.timeout,
        stream=False,
    )

    errors.APIError.raise_for_response(response)
    return HttpResponse(response.headers, byte_stream=[response.content])

  async def async_upload_file(
      self,
      file_path: Union[str, io.IOBase],
      upload_url: str,
      upload_size: int,
  ) -> str:
    """Transfers a file asynchronously to the given URL.

    Args:
      file_path: The full path to the file. If the local file path is not found,
        an error will be raised.
      upload_url: The URL to upload the file to.
      upload_size: The size of file content to be uploaded, this will have to
        match the size requested in the resumable upload request.

    returns:
          The response json object from the finalize request.
    """
    return await asyncio.to_thread(
        self.upload_file,
        file_path,
        upload_url,
        upload_size,
    )

  async def _async_upload_fd(
      self,
      file: io.IOBase,
      upload_url: str,
      upload_size: int,
  ) -> str:
    """Transfers a file asynchronously to the given URL.

    Args:
      file: A file like object inherited from io.BytesIO.
      upload_url: The URL to upload the file to.
      upload_size: The size of file content to be uploaded, this will have to
        match the size requested in the resumable upload request.

    returns:
          The response json object from the finalize request.
    """
    return await asyncio.to_thread(
        self._upload_fd,
        file,
        upload_url,
        upload_size,
    )

  async def async_download_file(self, path: str, http_options):
    """Downloads the file data.

    Args:
      path: The request path with query params.
      http_options: The http options to use for the request.

    returns:
          The file bytes
    """
    return await asyncio.to_thread(
        self.download_file,
        path,
        http_options,
    )

  # This method does nothing in the real api client. It is used in the
  # replay_api_client to verify the response from the SDK method matches the
  # recorded response.
  def _verify_response(self, response_model: BaseModel):
    pass
