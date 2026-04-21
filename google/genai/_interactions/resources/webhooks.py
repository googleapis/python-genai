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

from typing import List, Union
from typing_extensions import Literal

import httpx

from ..types import (
    webhook_list_params,
    webhook_ping_params,
    webhook_create_params,
    webhook_update_params,
    webhook_rotate_signing_secret_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import path_template, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.webhook import Webhook
from ..types.webhook_list_response import WebhookListResponse
from ..types.webhook_ping_response import WebhookPingResponse
from ..types.webhook_delete_response import WebhookDeleteResponse
from ..types.webhook_rotate_signing_secret_response import WebhookRotateSigningSecretResponse

__all__ = ["WebhooksResource", "AsyncWebhooksResource"]


class WebhooksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#accessing-raw-response-data-eg-headers
        """
        return WebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#with_streaming_response
        """
        return WebhooksResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_version: str | None = None,
        subscribed_events: List[
            Union[
                Literal[
                    "batch.succeeded",
                    "batch.cancelled",
                    "batch.expired",
                    "batch.failed",
                    "interaction.requires_action",
                    "interaction.completed",
                    "interaction.failed",
                    "interaction.cancelled",
                    "video.generated",
                ],
                str,
            ]
        ],
        uri: str,
        webhook_id: str | Omit = omit,
        name: str | Omit = omit,
        state: Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """Creates a new Webhook.

        Args:
          subscribed_events:
              Required.

        The events that the webhook is subscribed to. Available events:

              - batch.succeeded
              - batch.cancelled
              - batch.expired
              - batch.failed
              - interaction.requires_action
              - interaction.completed
              - interaction.failed
              - interaction.cancelled
              - video.generated

          uri: Required. The URI to which webhook events will be sent.

          webhook_id: Optional. The webhook_id to use for the webhook. If not specified, the server
              will generate a unique ID.

          name: Identifier. The name of the webhook. Format: `webhooks/{webhook_id}`

          state: The state of the webhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        return self._post(
            path_template("/{api_version}/webhooks", api_version=api_version),
            body=maybe_transform(
                {
                    "subscribed_events": subscribed_events,
                    "uri": uri,
                    "name": name,
                    "state": state,
                },
                webhook_create_params.WebhookCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"webhook_id": webhook_id}, webhook_create_params.WebhookCreateParams),
            ),
            cast_to=Webhook,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | None = None,
        subscribed_events: List[
            Union[
                Literal[
                    "batch.succeeded",
                    "batch.cancelled",
                    "batch.expired",
                    "batch.failed",
                    "interaction.requires_action",
                    "interaction.completed",
                    "interaction.failed",
                    "interaction.cancelled",
                    "video.generated",
                ],
                str,
            ]
        ],
        uri: str,
        update_mask: str | Omit = omit,
        name: str | Omit = omit,
        state: Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """Updates an existing Webhook.

        Args:
          subscribed_events:
              Required.

        The events that the webhook is subscribed to. Available events:

              - batch.succeeded
              - batch.cancelled
              - batch.expired
              - batch.failed
              - interaction.requires_action
              - interaction.completed
              - interaction.failed
              - interaction.cancelled
              - video.generated

          uri: Required. The URI to which webhook events will be sent.

          update_mask: Optional. The list of fields to update.

          name: Identifier. The name of the webhook. Format: `webhooks/{webhook_id}`

          state: The state of the webhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            body=maybe_transform(
                {
                    "subscribed_events": subscribed_events,
                    "uri": uri,
                    "name": name,
                    "state": state,
                },
                webhook_update_params.WebhookUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, webhook_update_params.WebhookUpdateParams),
            ),
            cast_to=Webhook,
        )

    def list(
        self,
        *,
        api_version: str | None = None,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookListResponse:
        """Lists all Webhooks.

        Args:
          page_size: Optional.

        The maximum number of webhooks to return. The service may return fewer
              than this value. If unspecified, at most 50 webhooks will be returned. The
              maximum value is 1000.

          page_token: Optional. A page token, received from a previous `ListWebhooks` call. Provide
              this to retrieve the subsequent page.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        return self._get(
            path_template("/{api_version}/webhooks", api_version=api_version),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    webhook_list_params.WebhookListParams,
                ),
            ),
            cast_to=WebhookListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookDeleteResponse:
        """
        Deletes a Webhook.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookDeleteResponse,
        )

    def get(
        self,
        id: str,
        *,
        api_version: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """
        Gets a specific Webhook.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Webhook,
        )

    def ping(
        self,
        id: str,
        *,
        api_version: str | None = None,
        body: webhook_ping_params.Body | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookPingResponse:
        """
        Sends a ping event to a Webhook.

        Args:
          body: Request message for WebhookService.PingWebhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            path_template("/{api_version}/webhooks/{id}:ping", api_version=api_version, id=id),
            body=maybe_transform(body, webhook_ping_params.WebhookPingParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookPingResponse,
        )

    def rotate_signing_secret(
        self,
        id: str,
        *,
        api_version: str | None = None,
        revocation_behavior: Literal["revoke_previous_secrets_after_h24", "revoke_previous_secrets_immediately"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookRotateSigningSecretResponse:
        """
        Generates a new signing secret for a Webhook.

        Args:
          revocation_behavior: Optional. The revocation behavior for previous signing secrets.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            path_template("/{api_version}/webhooks/{id}:rotateSigningSecret", api_version=api_version, id=id),
            body=maybe_transform(
                {"revocation_behavior": revocation_behavior},
                webhook_rotate_signing_secret_params.WebhookRotateSigningSecretParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookRotateSigningSecretResponse,
        )


class AsyncWebhooksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#with_streaming_response
        """
        return AsyncWebhooksResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_version: str | None = None,
        subscribed_events: List[
            Union[
                Literal[
                    "batch.succeeded",
                    "batch.cancelled",
                    "batch.expired",
                    "batch.failed",
                    "interaction.requires_action",
                    "interaction.completed",
                    "interaction.failed",
                    "interaction.cancelled",
                    "video.generated",
                ],
                str,
            ]
        ],
        uri: str,
        webhook_id: str | Omit = omit,
        name: str | Omit = omit,
        state: Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """Creates a new Webhook.

        Args:
          subscribed_events:
              Required.

        The events that the webhook is subscribed to. Available events:

              - batch.succeeded
              - batch.cancelled
              - batch.expired
              - batch.failed
              - interaction.requires_action
              - interaction.completed
              - interaction.failed
              - interaction.cancelled
              - video.generated

          uri: Required. The URI to which webhook events will be sent.

          webhook_id: Optional. The webhook_id to use for the webhook. If not specified, the server
              will generate a unique ID.

          name: Identifier. The name of the webhook. Format: `webhooks/{webhook_id}`

          state: The state of the webhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        return await self._post(
            path_template("/{api_version}/webhooks", api_version=api_version),
            body=await async_maybe_transform(
                {
                    "subscribed_events": subscribed_events,
                    "uri": uri,
                    "name": name,
                    "state": state,
                },
                webhook_create_params.WebhookCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"webhook_id": webhook_id}, webhook_create_params.WebhookCreateParams
                ),
            ),
            cast_to=Webhook,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | None = None,
        subscribed_events: List[
            Union[
                Literal[
                    "batch.succeeded",
                    "batch.cancelled",
                    "batch.expired",
                    "batch.failed",
                    "interaction.requires_action",
                    "interaction.completed",
                    "interaction.failed",
                    "interaction.cancelled",
                    "video.generated",
                ],
                str,
            ]
        ],
        uri: str,
        update_mask: str | Omit = omit,
        name: str | Omit = omit,
        state: Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """Updates an existing Webhook.

        Args:
          subscribed_events:
              Required.

        The events that the webhook is subscribed to. Available events:

              - batch.succeeded
              - batch.cancelled
              - batch.expired
              - batch.failed
              - interaction.requires_action
              - interaction.completed
              - interaction.failed
              - interaction.cancelled
              - video.generated

          uri: Required. The URI to which webhook events will be sent.

          update_mask: Optional. The list of fields to update.

          name: Identifier. The name of the webhook. Format: `webhooks/{webhook_id}`

          state: The state of the webhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            body=await async_maybe_transform(
                {
                    "subscribed_events": subscribed_events,
                    "uri": uri,
                    "name": name,
                    "state": state,
                },
                webhook_update_params.WebhookUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, webhook_update_params.WebhookUpdateParams
                ),
            ),
            cast_to=Webhook,
        )

    async def list(
        self,
        *,
        api_version: str | None = None,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookListResponse:
        """Lists all Webhooks.

        Args:
          page_size: Optional.

        The maximum number of webhooks to return. The service may return fewer
              than this value. If unspecified, at most 50 webhooks will be returned. The
              maximum value is 1000.

          page_token: Optional. A page token, received from a previous `ListWebhooks` call. Provide
              this to retrieve the subsequent page.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        return await self._get(
            path_template("/{api_version}/webhooks", api_version=api_version),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    webhook_list_params.WebhookListParams,
                ),
            ),
            cast_to=WebhookListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookDeleteResponse:
        """
        Deletes a Webhook.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookDeleteResponse,
        )

    async def get(
        self,
        id: str,
        *,
        api_version: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Webhook:
        """
        Gets a specific Webhook.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/{api_version}/webhooks/{id}", api_version=api_version, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Webhook,
        )

    async def ping(
        self,
        id: str,
        *,
        api_version: str | None = None,
        body: webhook_ping_params.Body | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookPingResponse:
        """
        Sends a ping event to a Webhook.

        Args:
          body: Request message for WebhookService.PingWebhook.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            path_template("/{api_version}/webhooks/{id}:ping", api_version=api_version, id=id),
            body=await async_maybe_transform(body, webhook_ping_params.WebhookPingParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookPingResponse,
        )

    async def rotate_signing_secret(
        self,
        id: str,
        *,
        api_version: str | None = None,
        revocation_behavior: Literal["revoke_previous_secrets_after_h24", "revoke_previous_secrets_immediately"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WebhookRotateSigningSecretResponse:
        """
        Generates a new signing secret for a Webhook.

        Args:
          revocation_behavior: Optional. The revocation behavior for previous signing secrets.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if api_version is None:
            api_version = self._client._get_api_version_path_param()
        if not api_version:
            raise ValueError(f"Expected a non-empty value for `api_version` but received {api_version!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            path_template("/{api_version}/webhooks/{id}:rotateSigningSecret", api_version=api_version, id=id),
            body=await async_maybe_transform(
                {"revocation_behavior": revocation_behavior},
                webhook_rotate_signing_secret_params.WebhookRotateSigningSecretParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookRotateSigningSecretResponse,
        )


class WebhooksResourceWithRawResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

        self.create = to_raw_response_wrapper(
            webhooks.create,
        )
        self.update = to_raw_response_wrapper(
            webhooks.update,
        )
        self.list = to_raw_response_wrapper(
            webhooks.list,
        )
        self.delete = to_raw_response_wrapper(
            webhooks.delete,
        )
        self.get = to_raw_response_wrapper(
            webhooks.get,
        )
        self.ping = to_raw_response_wrapper(
            webhooks.ping,
        )
        self.rotate_signing_secret = to_raw_response_wrapper(
            webhooks.rotate_signing_secret,
        )


class AsyncWebhooksResourceWithRawResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

        self.create = async_to_raw_response_wrapper(
            webhooks.create,
        )
        self.update = async_to_raw_response_wrapper(
            webhooks.update,
        )
        self.list = async_to_raw_response_wrapper(
            webhooks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            webhooks.delete,
        )
        self.get = async_to_raw_response_wrapper(
            webhooks.get,
        )
        self.ping = async_to_raw_response_wrapper(
            webhooks.ping,
        )
        self.rotate_signing_secret = async_to_raw_response_wrapper(
            webhooks.rotate_signing_secret,
        )


class WebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

        self.create = to_streamed_response_wrapper(
            webhooks.create,
        )
        self.update = to_streamed_response_wrapper(
            webhooks.update,
        )
        self.list = to_streamed_response_wrapper(
            webhooks.list,
        )
        self.delete = to_streamed_response_wrapper(
            webhooks.delete,
        )
        self.get = to_streamed_response_wrapper(
            webhooks.get,
        )
        self.ping = to_streamed_response_wrapper(
            webhooks.ping,
        )
        self.rotate_signing_secret = to_streamed_response_wrapper(
            webhooks.rotate_signing_secret,
        )


class AsyncWebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

        self.create = async_to_streamed_response_wrapper(
            webhooks.create,
        )
        self.update = async_to_streamed_response_wrapper(
            webhooks.update,
        )
        self.list = async_to_streamed_response_wrapper(
            webhooks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            webhooks.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            webhooks.get,
        )
        self.ping = async_to_streamed_response_wrapper(
            webhooks.ping,
        )
        self.rotate_signing_secret = async_to_streamed_response_wrapper(
            webhooks.rotate_signing_secret,
        )
