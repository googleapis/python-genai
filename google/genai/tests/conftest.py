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


"""Conftest for google.genai tests."""

import datetime
import os
from unittest import mock
import uuid
import pytest

from .. import _common
from .. import _replay_api_client
from .. import client as google_genai_client_module


def pytest_addoption(parser):
  parser.addoption(
      '--mode',
      action='store',
      default='auto',
      help="""Replay mode.
  One of:
  * auto: Replay if replay files exist, otherwise record.
  * record: Always call the API and record.
  * replay: Always replay, fail if replay files do not exist.
  * api: Always call the API and do not record.
  * tap: Always replay, fail if replay files do not exist. Also sets default values for the API key and replay directory.
""",
  )
  parser.addoption(
      '--private',
      action='store_true',
      default=False,
      help='Run private tests.',
  )


# Overridden via parameterized test.
@pytest.fixture
def use_vertex():
  return False


# Overridden at the module level for each test file.
@pytest.fixture
def replays_prefix():
  return 'test'


def _get_replay_id(use_vertex: bool, replays_prefix: str) -> str:
  test_name_ending = os.environ.get('PYTEST_CURRENT_TEST').split('::')[-1]
  test_name = (
      test_name_ending.split(' ')[0].split('[')[0]
      + '.'
      + ('vertex' if use_vertex else 'mldev')
  )
  return '/'.join([replays_prefix, test_name])


@pytest.fixture
def client(use_vertex, replays_prefix, http_options, request):
  mode = request.config.getoption('--mode')
  if mode not in ['auto', 'record', 'replay', 'api', 'tap']:
    raise ValueError('Invalid mode: ' + mode)
  test_function_name = request.function.__name__
  test_filename = os.path.splitext(os.path.basename(request.path))[0]
  if test_function_name.startswith(test_filename):
    raise ValueError(f"""
      {test_function_name}:
      Do not include the test filename in the test function name.
      keep the test function name short.""")
  for word in ['mldev', 'ml_dev', 'vertex']:
    if word in test_function_name:
      raise ValueError(f"""
        {test_function_name}:
        You should never ever include api types in the file name (mldev or vertex).
        All tests should run against all apis.
        Assert an exception if the test is not supported in an API.""")
  replay_id = _get_replay_id(use_vertex, replays_prefix)

  if mode == 'tap':
    mode = 'replay'

    # Set various environment variables to ensure that the test runs.
    os.environ['GOOGLE_API_KEY'] = 'dummy-api-key'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
        os.path.dirname(__file__),
        'credentials.json',
    )
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'project-id'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'location'

    # Set the replay directory to the root directory of the replays.
    # This is needed to ensure that the replay files are found.
    replays_root_directory = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../../../../../google/cloud/aiplatform/sdk/genai/replays',
        )
    )
    os.environ['GOOGLE_GENAI_REPLAYS_DIRECTORY'] = replays_root_directory
  # Get private arg.
  private = request.config.getoption('--private')
  replay_client = _replay_api_client.ReplayApiClient(
      mode=mode,
      replay_id=replay_id,
      vertexai=use_vertex,
      http_options=http_options,
      private=private,
  )

  with mock.patch.object(
      google_genai_client_module.Client, '_get_api_client'
  ) as patch_method:
    patch_method.return_value = replay_client
    google_genai_client = google_genai_client_module.Client(vertexai=use_vertex)

    # Yield the client so that cleanup can be completed at the end of the test.
    yield google_genai_client

    # Save the replay after the test if we were in recording mode.
    google_genai_client._api_client.close()


@pytest.fixture
def mock_timestamped_unique_name():
  with mock.patch.object(
      _common,
      'timestamped_unique_name',
      return_value='20240101000000_bd656',
  ) as unique_name_mock:
    yield unique_name_mock


@pytest.fixture
def image_jpeg():
  import PIL.Image
  image_path = os.path.join(os.path.dirname(__file__), 'data', 'google.jpg')
  with PIL.Image.open(image_path) as img:
    yield img


@pytest.fixture
def image_png():
  import PIL.Image
  image_path = os.path.join(os.path.dirname(__file__), 'data', 'google.png')
  with PIL.Image.open(image_path) as img:
    yield img
