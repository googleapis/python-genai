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
import json
import os
import sys
from typing import Any, Optional, TypedDict, Union
from urllib.parse import urlparse, urlunparse

import google.auth
import google.auth.credentials
from google.auth.transport.requests import AuthorizedSession
from pydantic import BaseModel
import requests

from . import errors


class HttpOptions(TypedDict):
  """HTTP options for the api client."""

  base_url: str = None
  """The base URL for the AI platform service endpoint."""
  api_version: str = None
  """Specifies the version of the API to use."""
  headers: dict[str, dict] = None
  """Additional HTTP headers to be sent with the request."""
  response_payload: dict = None
  """If set, the response payload will be returned int the supplied dict."""


def _append_library_version_headers(headers: dict[str, str]) -> None:
  """Appends the telemetry header to the headers dict."""
  # TODO: Automate revisions to the SDK library version.
  library_label = f'google-genai-sdk/0.2.2'
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
    options: HttpOptions, patch_options: HttpOptions
) -> HttpOptions:
  # use shallow copy so we don't override the original objects.
  copy_option = HttpOptions()
  copy_option.update(options)
  for k, v in patch_options.items():
    # if both are dicts, update the copy.
    # This is to handle cases like merging headers.
    if isinstance(v, dict) and isinstance(copy_option.get(k, None), dict):
      copy_option[k] = {}
      copy_option[k].update(options[k])  # shallow copy from original options.
      copy_option[k].update(v)
    elif v is not None:  # Accept empty values.
      copy_option[k] = v
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


class HttpResponse:

  def __init__(self, headers: dict[str, str], response_stream: Union[Any, str]):
    self.status_code = 200
    self.headers = headers
    self.response_stream = response_stream

  @property
  def text(self) -> str:
    if not self.response_stream[0]:  # Empty response
      return ''
    return json.loads(self.response_stream[0])

  def segments(self):
    if isinstance(self.response_stream, list):
      # list of objects retrieved from replay or from non-streaming API.
      for chunk in self.response_stream:
        yield json.loads(chunk) if chunk else {}
    else:
      # Iterator of objects retrieved from the API.
      for chunk in self.response_stream.iter_lines():
        if chunk:
          # In streaming mode, the chunk of JSON is prefixed with "data:" which
          # we must strip before parsing.
          if chunk.startswith(b'data: '):
            chunk = chunk[len(b'data: ') :]
          yield json.loads(str(chunk, 'utf-8'))

  def copy_to_dict(self, response_payload: dict[str, object]):
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
      http_options: HttpOptions = None,
  ):
    self.vertexai = vertexai
    if self.vertexai is None:
      if os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', '0').lower() in [
          'true',
          '1',
      ]:
        self.vertexai = True

    # Validate explicitly set intializer values.
    if (project or location) and api_key:
      raise ValueError(
          'Project/location and API key are mutually exclusive in the client initializer.'
      )

    self.api_key: Optional[str] = None
    self.project = project or os.environ.get('GOOGLE_CLOUD_PROJECT', None)
    self.location = location or os.environ.get('GOOGLE_CLOUD_LOCATION', None)
    self._credentials = credentials
    self._http_options = HttpOptions()

    if self.vertexai:
      if not self.project:
        self.project = google.auth.default()[1]
      # Will change this to support EasyGCP in the future.
      if not self.project or not self.location:
        raise ValueError(
            'Project and location must be set when using the Vertex AI API.'
        )
      self._http_options['base_url'] = (
          f'https://{self.location}-aiplatform.googleapis.com/'
      )
      self._http_options['api_version'] = 'v1beta1'
    else:  # ML Dev API
      self.api_key = api_key or os.environ.get('GOOGLE_API_KEY', None)
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
      http_options: HttpOptions = None,
  ) -> HttpRequest:
    # Remove all special dict keys such as _url and _query.
    keys_to_delete = [key for key in request_dict.keys() if key.startswith('_')]
    for key in keys_to_delete:
      del request_dict[key]
    # patch the http options with the user provided settings.
    if http_options:
      patched_http_options = _patch_http_options(
          self._http_options, http_options
      )
    else:
      patched_http_options = self._http_options
    if self.vertexai and not path.startswith('projects/'):
      path = f'projects/{self.project}/locations/{self.location}/' + path
    url = _join_url_path(
        patched_http_options['base_url'],
        patched_http_options['api_version'] + '/' + path,
    )
    return HttpRequest(
        method=http_method,
        url=url,
        headers=patched_http_options['headers'],
        data=request_dict,
    )

  def _request(
      self,
      http_request: HttpRequest,
      stream: bool = False,
  ) -> HttpResponse:
    if self.vertexai:
      if not self._credentials:
        self._credentials, _ = google.auth.default()
      authed_session = AuthorizedSession(self._credentials)
      authed_session.stream = stream
      response = authed_session.request(
          http_request.method.upper(),
          http_request.url,
          headers=http_request.headers,
          data=json.dumps(http_request.data, cls=RequestJsonEncoder) if http_request.data else None,
          # TODO: support timeout in RequestOptions so it can be configured
          # per methods.
          timeout=None,
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
        data = json.dumps(http_request.data, cls=RequestJsonEncoder)
      else:
        data = http_request.data

    http_session = requests.Session()
    request = requests.Request(
        method=http_request.method,
        url=http_request.url,
        headers=http_request.headers,
        data=data,
    ).prepare()
    response = http_session.send(request, stream=stream)
    errors.APIError.raise_for_response(response)
    return HttpResponse(
        response.headers, response if stream else [response.text]
    )

  async def _async_request(
      self, http_request: HttpRequest, stream: bool = False
  ):
    if self.vertexai:
      if not self._credentials:
        self._credentials, _ = google.auth.default()
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

  def get_read_only_http_options(self) -> HttpOptions:
    copied = HttpOptions()
    copied.update(self._http_options)
    return copied

  def request(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptions = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )
    response = self._request(http_request, stream=False)
    if http_options and 'response_payload' in http_options:
      response.copy_to_dict(http_options['response_payload'])
    return response.text

  def request_streamed(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptions = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    session_response = self._request(http_request, stream=True)
    if http_options and 'response_payload' in http_options:
      session_response.copy_to_dict(http_options['response_payload'])
    for chunk in session_response.segments():
      yield chunk

  async def async_request(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptions = None,
  ) -> dict[str, object]:
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    result = await self._async_request(http_request=http_request, stream=False)
    if http_options and 'response_payload' in http_options:
      result.copy_to_dict(http_options['response_payload'])
    return result.text

  async def async_request_streamed(
      self,
      http_method: str,
      path: str,
      request_dict: dict[str, object],
      http_options: HttpOptions = None,
  ):
    http_request = self._build_request(
        http_method, path, request_dict, http_options
    )

    response = await self._async_request(http_request=http_request, stream=True)

    for chunk in response.segments():
      yield chunk
    if http_options and 'response_payload' in http_options:
      response.copy_to_dict(http_options['response_payload'])

  def upload_file(self, file_path: str, upload_url: str, upload_size: int):
    """Transfers a file to the given URL.

    Args:
      file_path: The full path to the file. If the local file path is not found,
        an error will be raised.
      upload_url: The URL to upload the file to.
      upload_size: The size of file content to be uploaded, this will have to
        match the size requested in the resumable upload request.

    returns:
          The response json object from the finalize request.
    """
    offset = 0
    # Upload the file in chunks
    with open(file_path, 'rb') as file:
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
              f' finalized. {response.headers}, body: {response.text}'
          )

    if response.headers['X-Goog-Upload-Status'] != 'final':
      raise ValueError(
          'Failed to upload file: Upload status is not finalized. headers:'
          f' {response.headers}, body: {response.text}'
      )
    return response.text

  async def async_upload_file(
      self,
      file_path: str,
      upload_url: str,
      upload_size: int,
  ):
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

  # This method does nothing in the real api client. It is used in the
  # replay_api_client to verify the response from the SDK method matches the
  # recorded response.
  def _verify_response(self, response_model: BaseModel):
    pass


class RequestJsonEncoder(json.JSONEncoder):
  """Encode bytes as strings without modify its content."""

  def default(self, o):
    if isinstance(o, bytes):
      return o.decode()
    elif isinstance(o, datetime.datetime):
      # This Zulu time format is used by the Vertex AI API and the test recorder
      # Using strftime works well, but we want to align with the replay encoder.
      # o.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      return o.isoformat().replace('+00:00', 'Z')
    else:
      return super().default(o)
