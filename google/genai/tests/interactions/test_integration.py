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

from unittest import mock
import pytest
from ... import client as client_lib

pytest_plugins = ("pytest_asyncio",)


def test_client_future_warning():
  with mock.patch.object(
      client_lib, "_interactions_experimental_warned", new=False
  ):
    client = client_lib.Client(
        api_key="placeholder",
        http_options={
            "api_version": "v1alpha",
        }
    )
    with pytest.warns(
        UserWarning, match="Interactions.*experimental"
    ):
      _ = client.interactions


def test_client_timeout():
  with mock.patch.object(
      client_lib, "GeminiNextGenAPIClient", spec_set=True
  ) as mock_nextgen_client:

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    _ = client.interactions

    mock_nextgen_client.assert_called_once_with(
        base_url=mock.ANY,
        api_key="placeholder",
        api_version="v1alpha",
        default_headers=mock.ANY,
        http_client=mock.ANY,
        timeout=5.0,
        max_retries=mock.ANY,
        client_adapter=mock.ANY,
    )


@pytest.mark.asyncio
async def test_async_client_timeout():
  with mock.patch.object(
      client_lib, "AsyncGeminiNextGenAPIClient", spec_set=True
  ) as mock_nextgen_client:

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    _ = client.aio.interactions

    mock_nextgen_client.assert_called_once_with(
        base_url=mock.ANY,
        api_key="placeholder",
        api_version="v1alpha",
        default_headers=mock.ANY,
        http_client=mock.ANY,
        timeout=5.0,
        max_retries=mock.ANY,
        client_adapter=mock.ANY,
    )
