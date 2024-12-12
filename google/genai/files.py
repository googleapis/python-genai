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

import mimetypes
import os
from typing import Optional, Union
from urllib.parse import urlencode
from . import _common
from . import _transformers as t
from . import types
from ._api_client import ApiClient
from ._common import get_value_by_path as getv
from ._common import set_value_by_path as setv
from .pagers import AsyncPager, Pager


def _ListFilesConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['page_size']) is not None:
    setv(
        parent_object, ['_query', 'pageSize'], getv(from_object, ['page_size'])
    )

  if getv(from_object, ['page_token']) is not None:
    setv(
        parent_object,
        ['_query', 'pageToken'],
        getv(from_object, ['page_token']),
    )

  return to_object


def _ListFilesConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  if getv(from_object, ['page_size']) is not None:
    setv(
        parent_object, ['_query', 'pageSize'], getv(from_object, ['page_size'])
    )

  if getv(from_object, ['page_token']) is not None:
    setv(
        parent_object,
        ['_query', 'pageToken'],
        getv(from_object, ['page_token']),
    )

  return to_object


def _ListFilesParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _ListFilesConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _ListFilesParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['config']):
    raise ValueError('config parameter is not supported in Vertex AI.')

  return to_object


def _FileStatus_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['details']) is not None:
    setv(to_object, ['details'], getv(from_object, ['details']))

  if getv(from_object, ['message']) is not None:
    setv(to_object, ['message'], getv(from_object, ['message']))

  if getv(from_object, ['code']) is not None:
    setv(to_object, ['code'], getv(from_object, ['code']))

  return to_object


def _FileStatus_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['details']):
    raise ValueError('details parameter is not supported in Vertex AI.')

  if getv(from_object, ['message']):
    raise ValueError('message parameter is not supported in Vertex AI.')

  if getv(from_object, ['code']):
    raise ValueError('code parameter is not supported in Vertex AI.')

  return to_object


def _File_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['display_name']) is not None:
    setv(to_object, ['displayName'], getv(from_object, ['display_name']))

  if getv(from_object, ['mime_type']) is not None:
    setv(to_object, ['mimeType'], getv(from_object, ['mime_type']))

  if getv(from_object, ['size_bytes']) is not None:
    setv(to_object, ['sizeBytes'], getv(from_object, ['size_bytes']))

  if getv(from_object, ['create_time']) is not None:
    setv(to_object, ['createTime'], getv(from_object, ['create_time']))

  if getv(from_object, ['expiration_time']) is not None:
    setv(to_object, ['expirationTime'], getv(from_object, ['expiration_time']))

  if getv(from_object, ['update_time']) is not None:
    setv(to_object, ['updateTime'], getv(from_object, ['update_time']))

  if getv(from_object, ['sha256_hash']) is not None:
    setv(to_object, ['sha256Hash'], getv(from_object, ['sha256_hash']))

  if getv(from_object, ['uri']) is not None:
    setv(to_object, ['uri'], getv(from_object, ['uri']))

  if getv(from_object, ['state']) is not None:
    setv(to_object, ['state'], getv(from_object, ['state']))

  if getv(from_object, ['video_metadata']) is not None:
    setv(to_object, ['videoMetadata'], getv(from_object, ['video_metadata']))

  if getv(from_object, ['error']) is not None:
    setv(
        to_object,
        ['error'],
        _FileStatus_to_mldev(
            api_client, getv(from_object, ['error']), to_object
        ),
    )

  return to_object


def _File_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']):
    raise ValueError('name parameter is not supported in Vertex AI.')

  if getv(from_object, ['display_name']):
    raise ValueError('display_name parameter is not supported in Vertex AI.')

  if getv(from_object, ['mime_type']):
    raise ValueError('mime_type parameter is not supported in Vertex AI.')

  if getv(from_object, ['size_bytes']):
    raise ValueError('size_bytes parameter is not supported in Vertex AI.')

  if getv(from_object, ['create_time']):
    raise ValueError('create_time parameter is not supported in Vertex AI.')

  if getv(from_object, ['expiration_time']):
    raise ValueError('expiration_time parameter is not supported in Vertex AI.')

  if getv(from_object, ['update_time']):
    raise ValueError('update_time parameter is not supported in Vertex AI.')

  if getv(from_object, ['sha256_hash']):
    raise ValueError('sha256_hash parameter is not supported in Vertex AI.')

  if getv(from_object, ['uri']):
    raise ValueError('uri parameter is not supported in Vertex AI.')

  if getv(from_object, ['state']):
    raise ValueError('state parameter is not supported in Vertex AI.')

  if getv(from_object, ['video_metadata']):
    raise ValueError('video_metadata parameter is not supported in Vertex AI.')

  if getv(from_object, ['error']):
    raise ValueError('error parameter is not supported in Vertex AI.')

  return to_object


def _CreateFileConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _CreateFileConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _CreateFileParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['file']) is not None:
    setv(
        to_object,
        ['file'],
        _File_to_mldev(api_client, getv(from_object, ['file']), to_object),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _CreateFileConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _CreateFileParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['file']):
    raise ValueError('file parameter is not supported in Vertex AI.')

  if getv(from_object, ['config']):
    raise ValueError('config parameter is not supported in Vertex AI.')

  return to_object


def _GetFileConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _GetFileConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _GetFileParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(
        to_object,
        ['_url', 'file'],
        t.t_file_name(api_client, getv(from_object, ['name'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _GetFileConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _GetFileParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']):
    raise ValueError('name parameter is not supported in Vertex AI.')

  if getv(from_object, ['config']):
    raise ValueError('config parameter is not supported in Vertex AI.')

  return to_object


def _DeleteFileConfig_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _DeleteFileConfig_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['http_options']) is not None:
    setv(to_object, ['httpOptions'], getv(from_object, ['http_options']))

  return to_object


def _DeleteFileParameters_to_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(
        to_object,
        ['_url', 'file'],
        t.t_file_name(api_client, getv(from_object, ['name'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _DeleteFileConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _DeleteFileParameters_to_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']):
    raise ValueError('name parameter is not supported in Vertex AI.')

  if getv(from_object, ['config']):
    raise ValueError('config parameter is not supported in Vertex AI.')

  return to_object


def _FileStatus_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['details']) is not None:
    setv(to_object, ['details'], getv(from_object, ['details']))

  if getv(from_object, ['message']) is not None:
    setv(to_object, ['message'], getv(from_object, ['message']))

  if getv(from_object, ['code']) is not None:
    setv(to_object, ['code'], getv(from_object, ['code']))

  return to_object


def _FileStatus_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _File_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['name']) is not None:
    setv(to_object, ['name'], getv(from_object, ['name']))

  if getv(from_object, ['displayName']) is not None:
    setv(to_object, ['display_name'], getv(from_object, ['displayName']))

  if getv(from_object, ['mimeType']) is not None:
    setv(to_object, ['mime_type'], getv(from_object, ['mimeType']))

  if getv(from_object, ['sizeBytes']) is not None:
    setv(to_object, ['size_bytes'], getv(from_object, ['sizeBytes']))

  if getv(from_object, ['createTime']) is not None:
    setv(to_object, ['create_time'], getv(from_object, ['createTime']))

  if getv(from_object, ['expirationTime']) is not None:
    setv(to_object, ['expiration_time'], getv(from_object, ['expirationTime']))

  if getv(from_object, ['updateTime']) is not None:
    setv(to_object, ['update_time'], getv(from_object, ['updateTime']))

  if getv(from_object, ['sha256Hash']) is not None:
    setv(to_object, ['sha256_hash'], getv(from_object, ['sha256Hash']))

  if getv(from_object, ['uri']) is not None:
    setv(to_object, ['uri'], getv(from_object, ['uri']))

  if getv(from_object, ['state']) is not None:
    setv(to_object, ['state'], getv(from_object, ['state']))

  if getv(from_object, ['videoMetadata']) is not None:
    setv(to_object, ['video_metadata'], getv(from_object, ['videoMetadata']))

  if getv(from_object, ['error']) is not None:
    setv(
        to_object,
        ['error'],
        _FileStatus_from_mldev(
            api_client, getv(from_object, ['error']), to_object
        ),
    )

  return to_object


def _File_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _ListFilesResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}
  if getv(from_object, ['nextPageToken']) is not None:
    setv(to_object, ['next_page_token'], getv(from_object, ['nextPageToken']))

  if getv(from_object, ['files']) is not None:
    setv(
        to_object,
        ['files'],
        [
            _File_from_mldev(api_client, item, to_object)
            for item in getv(from_object, ['files'])
        ],
    )

  return to_object


def _ListFilesResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _CreateFileResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _CreateFileResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _DeleteFileResponse_from_mldev(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


def _DeleteFileResponse_from_vertex(
    api_client: ApiClient,
    from_object: Union[dict, object],
    parent_object: dict = None,
) -> dict:
  to_object = {}

  return to_object


class Files(_common.BaseModule):

  def _list(
      self, *, config: Optional[types.ListFilesConfigOrDict] = None
  ) -> types.ListFilesResponse:
    """Lists all files from the service.

    Args:
      config (ListFilesConfig): Optional, configuration for the list method.

    Returns:
      ListFilesResponse: The response for the list method.

    Usage:

    .. code-block:: python

      pager = client.files.list(config={'page_size': 10})
      for file in pager.page:
        print(file.name)
    """

    parameter_model = types._ListFilesParameters(
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _ListFilesParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ListFilesResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ListFilesResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ListFilesResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def _create(
      self,
      *,
      file: types.FileOrDict,
      config: Optional[types.CreateFileConfigOrDict] = None,
  ) -> types.CreateFileResponse:
    parameter_model = types._CreateFileParameters(
        file=file,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _CreateFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'upload/v1beta/files'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _CreateFileResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _CreateFileResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.CreateFileResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def get(
      self, *, name: str, config: Optional[types.GetFileConfigOrDict] = None
  ) -> types.File:
    """Retrieves the file information from the service.

    Args:
      name (str): The name identifier for the file to retrieve.
      config (GetFileConfig): Optional, configuration for the get method.

    Returns:
      File: The file information.

    Usage:

    .. code-block:: python

      file = client.files.get(name='files/...')
      print(file.uri)
    """

    parameter_model = types._GetFileParameters(
        name=name,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _GetFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files/{file}'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _File_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _File_from_mldev(self.api_client, response_dict)

    return_value = types.File._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  def delete(
      self, *, name: str, config: Optional[types.DeleteFileConfigOrDict] = None
  ) -> types.DeleteFileResponse:
    """Deletes an existing file from the service.

    Args:
      name (str): The name identifier for the file to delete.
      config (DeleteFileConfig): Optional, configuration for the delete method.

    Returns:
      DeleteFileResponse: The response for the delete method

    Usage:

    .. code-block:: python

      client.files.delete(name='files/...')
    """

    parameter_model = types._DeleteFileParameters(
        name=name,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _DeleteFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files/{file}'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = self.api_client.request(
        'delete', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _DeleteFileResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _DeleteFileResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.DeleteFileResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  def upload(
      self,
      *,
      path: str,
      config: Optional[types.UploadFileConfigOrDict] = None,
  ) -> types.File:
    """Calls the API to upload a file using a supported file service.

    Args:
      path: The path to the file or a file-like object (e.g. `BytesIO`) to be
        uploaded.
      config: Optional parameters to set `diplay_name`, `mime_type`, and `name`.
    """
    if self.api_client.vertexai:
      raise ValueError(
          'Vertex AI does not support creating files. You can upload files to'
          ' GCS files instead.'
      )
    config_model = None
    if config:
      if isinstance(config, dict):
        config_model = types.UploadFileConfig(**config)
      else:
        config_model = config
      file = types.File(
          mime_type=config_model.mime_type,
          name=config_model.name,
          display_name=config_model.display_name,
      )
    else:  # if not config
      file = types.File()
    if file.name is not None and not file.name.startswith('files/'):
      file.name = f'files/{file.name}'

    fs_path = os.fspath(path)
    if not fs_path or not os.path.isfile(fs_path):
      raise FileNotFoundError(f'{path} is not a valid file path.')
    file.size_bytes = os.path.getsize(fs_path)
    if file.mime_type is None:
      file.mime_type, _ = mimetypes.guess_type(fs_path)
    if file.mime_type is None:
      raise ValueError(
          'Unknown mime type: Could not determine the mimetype for your file\n'
          '    please set the `mime_type` argument'
      )
    response = {}
    if config_model and config_model.http_options:
      http_options = config_model.http_options
    else:
      http_options = {
          'api_version': '',  # api-version is set in the path.
          'headers': {
              'Content-Type': 'application/json',
              'X-Goog-Upload-Protocol': 'resumable',
              'X-Goog-Upload-Command': 'start',
              'X-Goog-Upload-Header-Content-Length': f'{file.size_bytes}',
              'X-Goog-Upload-Header-Content-Type': f'{file.mime_type}',
          },
          'response_payload': response,
      }
    self._create(file=file, config={'http_options': http_options})
    if (
        'headers' not in response
        or 'X-Goog-Upload-URL' not in response['headers']
    ):
      raise KeyError(
          'Failed to create file. Upload URL did not returned from the create'
          ' file request.'
      )
    upload_url = response['headers']['X-Goog-Upload-URL']

    return_file = self.api_client.upload_file(
        fs_path, upload_url, file.size_bytes
    )

    return types.File._from_response(
        _File_from_mldev(self.api_client, return_file['file']), None
    )

  def list(
      self, *, config: Optional[types.ListFilesConfigOrDict] = None
  ) -> Pager[types.File]:
    return Pager(
        'files',
        self._list,
        self._list(config=config),
        config,
    )


class AsyncFiles(_common.BaseModule):

  async def _list(
      self, *, config: Optional[types.ListFilesConfigOrDict] = None
  ) -> types.ListFilesResponse:
    """Lists all files from the service.

    Args:
      config (ListFilesConfig): Optional, configuration for the list method.

    Returns:
      ListFilesResponse: The response for the list method.

    Usage:

    .. code-block:: python

      pager = client.files.list(config={'page_size': 10})
      for file in pager.page:
        print(file.name)
    """

    parameter_model = types._ListFilesParameters(
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _ListFilesParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _ListFilesResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _ListFilesResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.ListFilesResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def _create(
      self,
      *,
      file: types.FileOrDict,
      config: Optional[types.CreateFileConfigOrDict] = None,
  ) -> types.CreateFileResponse:
    parameter_model = types._CreateFileParameters(
        file=file,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _CreateFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'upload/v1beta/files'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'post', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _CreateFileResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _CreateFileResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.CreateFileResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def get(
      self, *, name: str, config: Optional[types.GetFileConfigOrDict] = None
  ) -> types.File:
    """Retrieves the file information from the service.

    Args:
      name (str): The name identifier for the file to retrieve.
      config (GetFileConfig): Optional, configuration for the get method.

    Returns:
      File: The file information.

    Usage:

    .. code-block:: python

      file = client.files.get(name='files/...')
      print(file.uri)
    """

    parameter_model = types._GetFileParameters(
        name=name,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _GetFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files/{file}'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'get', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _File_from_vertex(self.api_client, response_dict)
    else:
      response_dict = _File_from_mldev(self.api_client, response_dict)

    return_value = types.File._from_response(response_dict, parameter_model)
    self.api_client._verify_response(return_value)
    return return_value

  async def delete(
      self, *, name: str, config: Optional[types.DeleteFileConfigOrDict] = None
  ) -> types.DeleteFileResponse:
    """Deletes an existing file from the service.

    Args:
      name (str): The name identifier for the file to delete.
      config (DeleteFileConfig): Optional, configuration for the delete method.

    Returns:
      DeleteFileResponse: The response for the delete method

    Usage:

    .. code-block:: python

      client.files.delete(name='files/...')
    """

    parameter_model = types._DeleteFileParameters(
        name=name,
        config=config,
    )

    if self.api_client.vertexai:
      raise ValueError('This method is only supported in the default client.')
    else:
      request_dict = _DeleteFileParameters_to_mldev(
          self.api_client, parameter_model
      )
      path = 'files/{file}'.format_map(request_dict.get('_url'))

    query_params = request_dict.get('_query')
    if query_params:
      path = f'{path}?{urlencode(query_params)}'
    # TODO: remove the hack that pops config.
    config = request_dict.pop('config', None)
    http_options = config.pop('httpOptions', None) if config else None
    request_dict = _common.convert_to_dict(request_dict)
    request_dict = _common.apply_base64_encoding(request_dict)

    response_dict = await self.api_client.async_request(
        'delete', path, request_dict, http_options
    )

    if self.api_client.vertexai:
      response_dict = _DeleteFileResponse_from_vertex(
          self.api_client, response_dict
      )
    else:
      response_dict = _DeleteFileResponse_from_mldev(
          self.api_client, response_dict
      )

    return_value = types.DeleteFileResponse._from_response(
        response_dict, parameter_model
    )
    self.api_client._verify_response(return_value)
    return return_value

  async def upload(
      self,
      *,
      path: str,
      config: Optional[types.UploadFileConfigOrDict] = None,
  ) -> types.File:
    """Calls the API to upload a file asynchronously using a supported file service.

    Args:
      path: The path to the file or a file-like object (e.g. `BytesIO`) to be
        uploaded.
      config: Optional parameters to set `diplay_name`, `mime_type`, and `name`.
    """
    if self.api_client.vertexai:
      raise ValueError(
          'Vertex AI does not support creating files. You can upload files to'
          ' GCS files instead.'
      )
    config_model = None
    if config:
      if isinstance(config, dict):
        config_model = types.UploadFileConfig(**config)
      else:
        config_model = config
      file = types.File(
          mime_type=config_model.mime_type,
          name=config_model.name,
          display_name=config_model.display_name,
      )
    else:  # if not config
      file = types.File()
    if file.name is not None and not file.name.startswith('files/'):
      file.name = f'files/{file.name}'

    fs_path = os.fspath(path)
    if not fs_path or not os.path.isfile(fs_path):
      raise FileNotFoundError(f'{path} is not a valid file path.')
    file.size_bytes = os.path.getsize(fs_path)
    if file.mime_type is None:
      file.mime_type, _ = mimetypes.guess_type(fs_path)
    if file.mime_type is None:
      raise ValueError(
          'Unknown mime type: Could not determine the mimetype for your file\n'
          '    please set the `mime_type` argument'
      )
    response = {}
    if config_model and config_model.http_options:
      http_options = config_model.http_options
    else:
      http_options = {
          'api_version': '',  # api-version is set in the path.
          'headers': {
              'Content-Type': 'application/json',
              'X-Goog-Upload-Protocol': 'resumable',
              'X-Goog-Upload-Command': 'start',
              'X-Goog-Upload-Header-Content-Length': f'{file.size_bytes}',
              'X-Goog-Upload-Header-Content-Type': f'{file.mime_type}',
          },
          'response_payload': response,
      }
    await self._create(file=file, config={'http_options': http_options})
    if (
        'headers' not in response
        or 'X-Goog-Upload-URL' not in response['headers']
    ):
      raise KeyError(
          'Failed to create file. Upload URL did not returned from the create'
          ' file request.'
      )
    upload_url = response['headers']['X-Goog-Upload-URL']

    return_file = await self.api_client.async_upload_file(
        fs_path, upload_url, file.size_bytes
    )

    return types.File._from_response(
        _File_from_mldev(self.api_client, return_file['file']), None
    )

  async def list(
      self, *, config: Optional[types.ListFilesConfigOrDict] = None
  ) -> AsyncPager[types.File]:
    return AsyncPager(
        'files',
        self._list,
        await self._list(config=config),
        config,
    )
