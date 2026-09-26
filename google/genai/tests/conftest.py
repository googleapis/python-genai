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
from .. import types


# Retry options for the shared integration tests, applied to every request the
# test client makes so that a transient 5xx or 429 does not fail the nightly.
#
# Deliberately shorter than the SDK defaults: a multistep test retries per
# request, so the backoff has to stay well inside the test timeout. Keep aligned with
# the shared test clients in the other SDKs.
_SHARED_TEST_RETRY_OPTIONS = types.HttpRetryOptions(
    attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exp_base=2.0,
    http_status_codes=[408, 429, 500, 502, 503, 504],
)


def _is_shared_integration_test(request):
  """True only for the curated cross-SDK suite under tests/shared."""
  return 'shared' in os.fspath(request.path).split(os.sep)


def _with_shared_test_retry_options(http_options):
  """Adds the shared retry options, leaving any caller-supplied ones alone."""
  if http_options is None:
    return types.HttpOptions(retry_options=_SHARED_TEST_RETRY_OPTIONS)
  if isinstance(http_options, dict):
    if http_options.get('retry_options') or http_options.get('retryOptions'):
      return http_options
    return {**http_options, 'retry_options': _SHARED_TEST_RETRY_OPTIONS}
  if getattr(http_options, 'retry_options', None):
    return http_options
  return http_options.model_copy(
      update={'retry_options': _SHARED_TEST_RETRY_OPTIONS}
  )


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


@pytest.fixture(autouse=True)
def skip_based_on_api_mode_env_vars(request):
  mode = request.config.getoption('--mode')
  if mode == 'api':
    use_vertex = None
    if hasattr(request, 'node') and hasattr(request.node, 'callspec'):
      use_vertex = request.node.callspec.params.get('use_vertex')
    elif 'use_vertex' in request.fixturenames:
      use_vertex = request.getfixturevalue('use_vertex')

    run_vertex_only = os.environ.get('GOOGLE_GENAI_RUN_VERTEX_ONLY_IN_API_MODE')
    run_gemini_only = os.environ.get('GOOGLE_GENAI_RUN_GEMINI_ONLY_IN_API_MODE')

    if use_vertex is True and run_gemini_only:
      pytest.skip('Skipping Vertex AI tests in API mode (GEMINI ONLY config enabled).')
    elif use_vertex is False and run_vertex_only:
      pytest.skip('Skipping Gemini API tests in API mode (VERTEX ONLY config enabled).')


# Overridden at the module level for each test file.
@pytest.fixture
def replays_prefix():
  return 'test'


# Overridden by test packages whose Vertex model is not served at the configured
# location. Returning None leaves GOOGLE_CLOUD_LOCATION as-is.
@pytest.fixture
def location_override():
  return None


def _get_replay_id(use_vertex: bool, replays_prefix: str) -> str:
  test_name_ending = os.environ.get('PYTEST_CURRENT_TEST').split('::')[-1]
  test_name = (
      test_name_ending.split(' ')[0].split('[')[0]
      + '.'
      + ('vertex' if use_vertex else 'mldev')
  )
  return '/'.join([replays_prefix, test_name])


@pytest.fixture
def client(use_vertex, replays_prefix, http_options, request, location_override):
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

  if not use_vertex:
    location_override = None
  elif location_override is None and 'tunings' in replays_prefix:
    # Tuning jobs are not supported on the global endpoint.
    if os.environ.get('GOOGLE_CLOUD_LOCATION') == 'global':
      location_override = 'us-central1'

  # Scoped to the shared suite rather than all of api mode, so no other test's
  # behaviour changes.
  if mode == 'api' and _is_shared_integration_test(request):
    http_options = _with_shared_test_retry_options(http_options)

  replay_client = _replay_api_client.ReplayApiClient(
      mode=mode,
      replay_id=replay_id,
      vertexai=use_vertex,
      http_options=http_options,
      private=private,
      location=location_override,
  )

  with mock.patch.object(
      google_genai_client_module.Client, '_get_api_client'
  ) as patch_method:
    patch_method.return_value = replay_client
    kwargs = {'vertexai': use_vertex}
    if location_override:
      kwargs['location'] = location_override
    google_genai_client = google_genai_client_module.Client(**kwargs)

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
