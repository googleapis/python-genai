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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from google.genai._interactions import GeminiNextGenAPIClient, AsyncGeminiNextGenAPIClient
from google.genai._interactions.types import (
    Webhook,
    WebhookListResponse,
    WebhookPingResponse,
    WebhookDeleteResponse,
    WebhookRotateSigningSecretResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhooks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
            name="name",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.create(
                api_version="",
                subscribed_events=["batch.succeeded"],
                uri="uri",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_update(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.update(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.update(
            id="id",
            api_version="api_version",
            update_mask="update_mask",
            name="name",
            state="enabled",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.update(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.update(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_update(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.update(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhooks.with_raw_response.update(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.list(
            api_version="api_version",
        )
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.list(
            api_version="api_version",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.list(
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.list(
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(WebhookListResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.list(
                api_version="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.delete(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.delete(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.delete(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.delete(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhooks.with_raw_response.delete(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.get(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.get(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.get(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.get(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhooks.with_raw_response.get(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_ping(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.ping(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_ping_with_all_params(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.ping(
            id="id",
            api_version="api_version",
            body={},
        )
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_ping(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.ping(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_ping(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.ping(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(WebhookPingResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_ping(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.ping(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhooks.with_raw_response.ping(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_rotate_signing_secret(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.rotate_signing_secret(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_rotate_signing_secret_with_all_params(self, client: GeminiNextGenAPIClient) -> None:
        webhook = client.webhooks.rotate_signing_secret(
            id="id",
            api_version="api_version",
            revocation_behavior="revoke_previous_secrets_after_h24",
        )
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_rotate_signing_secret(self, client: GeminiNextGenAPIClient) -> None:
        response = client.webhooks.with_raw_response.rotate_signing_secret(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = response.parse()
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_rotate_signing_secret(self, client: GeminiNextGenAPIClient) -> None:
        with client.webhooks.with_streaming_response.rotate_signing_secret(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = response.parse()
            assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_rotate_signing_secret(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.webhooks.with_raw_response.rotate_signing_secret(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.webhooks.with_raw_response.rotate_signing_secret(
                id="",
                api_version="api_version",
            )


class TestAsyncWebhooks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
            name="name",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.create(
            api_version="api_version",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.create(
                api_version="",
                subscribed_events=["batch.succeeded"],
                uri="uri",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.update(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.update(
            id="id",
            api_version="api_version",
            update_mask="update_mask",
            name="name",
            state="enabled",
            subscribed_events=["batch.succeeded"],
            uri="uri",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.update(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.update(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.update(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhooks.with_raw_response.update(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.list(
            api_version="api_version",
        )
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.list(
            api_version="api_version",
            page_size=0,
            page_token="page_token",
        )
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.list(
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(WebhookListResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.list(
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(WebhookListResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.list(
                api_version="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.delete(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.delete(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.delete(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(WebhookDeleteResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.delete(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhooks.with_raw_response.delete(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.get(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.get(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(Webhook, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.get(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(Webhook, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.get(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhooks.with_raw_response.get(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_ping(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.ping(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_ping_with_all_params(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.ping(
            id="id",
            api_version="api_version",
            body={},
        )
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.ping(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(WebhookPingResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.ping(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(WebhookPingResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_ping(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.ping(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhooks.with_raw_response.ping(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_rotate_signing_secret(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        webhook = await async_client.webhooks.rotate_signing_secret(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_rotate_signing_secret_with_all_params(
        self, async_client: AsyncGeminiNextGenAPIClient
    ) -> None:
        webhook = await async_client.webhooks.rotate_signing_secret(
            id="id",
            api_version="api_version",
            revocation_behavior="revoke_previous_secrets_after_h24",
        )
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_rotate_signing_secret(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.webhooks.with_raw_response.rotate_signing_secret(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        webhook = await response.parse()
        assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_rotate_signing_secret(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.webhooks.with_streaming_response.rotate_signing_secret(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            webhook = await response.parse()
            assert_matches_type(WebhookRotateSigningSecretResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_rotate_signing_secret(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.webhooks.with_raw_response.rotate_signing_secret(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.webhooks.with_raw_response.rotate_signing_secret(
                id="",
                api_version="api_version",
            )
