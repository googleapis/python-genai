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


"""Test files get method."""

import pytest
from ... import types
from ... import Client
from ... import _api_client
from .. import pytest_helper
import google.auth


# $ gcloud config set project vertex-sdk-dev
# $ gcloud auth application-default login --no-launch-browser --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/devstorage.read_only"
def get_headers():
  try:
    credentials, _ = google.auth.default()
    token = _api_client.get_token_from_credentials(None, credentials)
    headers = {
      "Authorization": f"Bearer {token}",}
    if credentials.quota_project_id:
      headers["x-goog-user-project"] = credentials.quota_project_id
  except google.auth.exceptions.DefaultCredentialsError:
    # So this can run in replay mode without credentials.
    headers = {}


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_register',
        parameters=types._RegisterFilesParameters(uris=['gs://unified-genai-dev/image.jpg']),
        exception_if_vertex='only supported in the Gemini Developer client',
        skip_in_api_mode=(
            'The files have a TTL, they cannot be reliably retrieved for a long'
            ' time.'
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='files._register_files',
    test_table=test_table,
    http_options={
        'headers': get_headers(),
    },
)


@pytest.mark.asyncio
async def test_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    files = await client.aio.files._register_files(uris=['gs://unified-genai-dev/image.jpg'])
    assert files.files
    assert files.files[0].mime_type == 'image/jpeg'
