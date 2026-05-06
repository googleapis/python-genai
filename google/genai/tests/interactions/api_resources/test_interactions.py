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
    Interaction,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInteractions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            background=True,
            generation_config={
                "image_config": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K",
                },
                "max_output_tokens": 0,
                "seed": 0,
                "speech_config": [
                    {
                        "language": "language",
                        "speaker": "speaker",
                        "voice": "voice",
                    }
                ],
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_level": "minimal",
                "thinking_summaries": "auto",
                "tool_choice": "auto",
                "top_p": 0,
            },
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            stream=False,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        )

        assert response.is_closed is True
        interaction = response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        ) as response:
            assert not response.is_closed

            interaction = response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.create(
                api_version="",
                input={
                    "text": "text",
                    "type": "text",
                },
                model="gemini-2.5-computer-use-preview-10-2025",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
            background=True,
            generation_config={
                "image_config": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K",
                },
                "max_output_tokens": 0,
                "seed": 0,
                "speech_config": [
                    {
                        "language": "language",
                        "speaker": "speaker",
                        "voice": "voice",
                    }
                ],
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_level": "minimal",
                "thinking_summaries": "auto",
                "tool_choice": "auto",
                "top_p": 0,
            },
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        )

        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.create(
                api_version="",
                input={
                    "text": "text",
                    "type": "text",
                },
                model="gemini-2.5-computer-use-preview-10-2025",
                stream=True,
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_overload_3(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_3(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            agent_config={"type": "dynamic"},
            background=True,
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            stream=False,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create_overload_3(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        )

        assert response.is_closed is True
        interaction = response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_3(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        ) as response:
            assert not response.is_closed

            interaction = response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create_overload_3(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.create(
                api_version="",
                agent="deep-research-pro-preview-12-2025",
                input={
                    "text": "text",
                    "type": "text",
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_overload_4(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_4(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            stream=True,
            agent_config={"type": "dynamic"},
            background=True,
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create_overload_4(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        )

        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_4(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create_overload_4(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.create(
                api_version="",
                agent="deep-research-pro-preview-12-2025",
                input={
                    "text": "text",
                    "type": "text",
                },
                stream=True,
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.delete(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(object, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.delete(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = response.parse()
        assert_matches_type(object, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.delete(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = response.parse()
            assert_matches_type(object, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.delete(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.interactions.with_raw_response.delete(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_cancel(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.cancel(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.cancel(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.cancel(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.cancel(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.interactions.with_raw_response.cancel(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.get(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_with_all_params_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        interaction = client.interactions.get(
            id="id",
            api_version="api_version",
            include_input=True,
            last_event_id="last_event_id",
            stream=False,
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.get(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.get(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_overload_1(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.get(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.interactions.with_raw_response.get(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.get(
            id="id",
            api_version="api_version",
            stream=True,
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_with_all_params_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        interaction_stream = client.interactions.get(
            id="id",
            api_version="api_version",
            stream=True,
            include_input=True,
            last_event_id="last_event_id",
        )
        interaction_stream.response.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        response = client.interactions.with_raw_response.get(
            id="id",
            api_version="api_version",
            stream=True,
        )

        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        with client.interactions.with_streaming_response.get(
            id="id",
            api_version="api_version",
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_overload_2(self, client: GeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            client.interactions.with_raw_response.get(
                id="id",
                api_version="",
                stream=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.interactions.with_raw_response.get(
                id="",
                api_version="api_version",
                stream=True,
            )


class TestAsyncInteractions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            background=True,
            generation_config={
                "image_config": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K",
                },
                "max_output_tokens": 0,
                "seed": 0,
                "speech_config": [
                    {
                        "language": "language",
                        "speaker": "speaker",
                        "voice": "voice",
                    }
                ],
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_level": "minimal",
                "thinking_summaries": "auto",
                "tool_choice": "auto",
                "top_p": 0,
            },
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            stream=False,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        )

        assert response.is_closed is True
        interaction = await response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
        ) as response:
            assert not response.is_closed

            interaction = await response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.create(
                api_version="",
                input={
                    "text": "text",
                    "type": "text",
                },
                model="gemini-2.5-computer-use-preview-10-2025",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
            background=True,
            generation_config={
                "image_config": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K",
                },
                "max_output_tokens": 0,
                "seed": 0,
                "speech_config": [
                    {
                        "language": "language",
                        "speaker": "speaker",
                        "voice": "voice",
                    }
                ],
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_level": "minimal",
                "thinking_summaries": "auto",
                "tool_choice": "auto",
                "top_p": 0,
            },
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        )

        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.create(
            api_version="api_version",
            input={
                "text": "text",
                "type": "text",
            },
            model="gemini-2.5-computer-use-preview-10-2025",
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.create(
                api_version="",
                input={
                    "text": "text",
                    "type": "text",
                },
                model="gemini-2.5-computer-use-preview-10-2025",
                stream=True,
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_overload_3(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_3(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            agent_config={"type": "dynamic"},
            background=True,
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            stream=False,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_3(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        )

        assert response.is_closed is True
        interaction = await response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_3(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
        ) as response:
            assert not response.is_closed

            interaction = await response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create_overload_3(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.create(
                api_version="",
                agent="deep-research-pro-preview-12-2025",
                input={
                    "text": "text",
                    "type": "text",
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_overload_4(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_4(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
                "annotations": [
                    {
                        "type": "url_citation",
                        "end_index": 0,
                        "start_index": 0,
                        "title": "title",
                        "url": "url",
                    }
                ],
            },
            stream=True,
            agent_config={"type": "dynamic"},
            background=True,
            previous_interaction_id="previous_interaction_id",
            response_format=[
                {
                    "type": "audio",
                    "bit_rate": 0,
                    "delivery": "inline",
                    "mime_type": "audio/mp3",
                    "sample_rate": 0,
                }
            ],
            response_mime_type="response_mime_type",
            response_modalities=["text"],
            service_tier="flex",
            store=True,
            system_instruction="system_instruction",
            tools=[
                {
                    "type": "function",
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                }
            ],
            webhook_config={
                "uris": ["string"],
                "user_metadata": {"foo": "bar"},
            },
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_4(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        )

        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_4(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.create(
            api_version="api_version",
            agent="deep-research-pro-preview-12-2025",
            input={
                "text": "text",
                "type": "text",
            },
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create_overload_4(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.create(
                api_version="",
                agent="deep-research-pro-preview-12-2025",
                input={
                    "text": "text",
                    "type": "text",
                },
                stream=True,
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.delete(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(object, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.delete(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = await response.parse()
        assert_matches_type(object, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.delete(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = await response.parse()
            assert_matches_type(object, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.delete(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.interactions.with_raw_response.delete(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.cancel(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.cancel(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = await response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.cancel(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = await response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.cancel(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.interactions.with_raw_response.cancel(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.get(
            id="id",
            api_version="api_version",
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_with_all_params_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction = await async_client.interactions.get(
            id="id",
            api_version="api_version",
            include_input=True,
            last_event_id="last_event_id",
            stream=False,
        )
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.get(
            id="id",
            api_version="api_version",
        )

        assert response.is_closed is True
        interaction = await response.parse()
        assert_matches_type(Interaction, interaction, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.get(
            id="id",
            api_version="api_version",
        ) as response:
            assert not response.is_closed

            interaction = await response.parse()
            assert_matches_type(Interaction, interaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_overload_1(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.get(
                id="id",
                api_version="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.interactions.with_raw_response.get(
                id="",
                api_version="api_version",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.get(
            id="id",
            api_version="api_version",
            stream=True,
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_with_all_params_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        interaction_stream = await async_client.interactions.get(
            id="id",
            api_version="api_version",
            stream=True,
            include_input=True,
            last_event_id="last_event_id",
        )
        await interaction_stream.response.aclose()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        response = await async_client.interactions.with_raw_response.get(
            id="id",
            api_version="api_version",
            stream=True,
        )

        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        async with async_client.interactions.with_streaming_response.get(
            id="id",
            api_version="api_version",
            stream=True,
        ) as response:
            assert not response.is_closed

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_overload_2(self, async_client: AsyncGeminiNextGenAPIClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `api_version` but received ''"):
            await async_client.interactions.with_raw_response.get(
                id="id",
                api_version="",
                stream=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.interactions.with_raw_response.get(
                id="",
                api_version="api_version",
                stream=True,
            )
