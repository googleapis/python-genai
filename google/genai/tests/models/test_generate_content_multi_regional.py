# Copyright 2026 Google LLC
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

import pytest

from ... import _replay_api_client
from ... import Client
from ...models import Models
from .. import pytest_helper


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
)


def test_eu_location_routing_prediction_replay(client, request, monkeypatch):
  """Tests that the SDK can route to the EU multi-regional endpoint."""
  if not client._api_client.vertexai:
    pytest.skip('Test requires Vertex AI')

  mode = request.config.getoption('--mode')
  if mode == 'tap':
    mode = 'replay'

  # The `client` fixture monkeypatches `Client._get_api_client` to always return
  # the fixture's client, which binds to `us-central1` via the environment.
  # To test `eu` routing, we bypass the mock by explicitly instantiating a
  # ReplayApiClient and injecting it.
  with monkeypatch.context() as m:
    m.delenv('GOOGLE_CLOUD_LOCATION', raising=False)

    replay_api_client = _replay_api_client.ReplayApiClient(
        mode=mode,
        replay_id='tests/models/generate_content_multi_regional/test_eu_location_routing_prediction_replay.vertex',
        replays_directory=os.environ.get('GOOGLE_GENAI_REPLAYS_DIRECTORY'),
        vertexai=True,
        project=client._api_client.project,
        location='eu',
    )

    eu_client = Client(vertexai=True)
    eu_client._api_client = replay_api_client
    eu_client._models = Models(replay_api_client)

    try:
      # 1. Verify that the SDK correctly resolved the EU REP base URL internally
      assert (
          eu_client._api_client._http_options.base_url
          == 'https://aiplatform.eu.rep.googleapis.com/'
      )

      # 2. Test the dataplane prediction (generate_content) against EU endpoint
      response = eu_client.models.generate_content(
          model='gemini-3-flash-preview',
          contents='Testing EU multi-regional endpoint routing.',
      )
      assert response is not None
    finally:
      eu_client.close()
