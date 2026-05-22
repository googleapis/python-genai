# Breaking changes: `client.fern_*` (Fern) vs `client.<x>` (Stainless `_interactions`)

This document enumerates the interface deltas between the **Fern‑generated** surface (exposed on `genai.Client` as `client.fern_interactions`, `client.fern_webhooks`, `client.fern_agents` via direct delegation in `google/genai/client.py`) and the **Stainless‑generated** surface (exposed as `client.interactions`, `client.webhooks`, `client.agents` and implemented under `google/genai/_interactions/`).

Source files compared:

- Fern client methods: `google/genai/_fern_interactions/fern_interactions/client.py`, `google/genai/_fern_interactions/fern_webhooks/client.py`, `google/genai/_fern_interactions/fern_agents/client.py`
- Fern accessor properties: `google/genai/client.py` (`AsyncClient.fern_interactions`, `SyncClient.fern_interactions`, etc. — direct delegation to `self._fern_nextgen_client.*`, no shim wrapper)
- Stainless resources: `google/genai/_interactions/resources/{interactions,webhooks,agents}.py`

The comparison is intentionally framed as "if I swap `client.fern_X` for `client.X`, what breaks?"

> **Note (architecture):** The shim wrapper classes (`_FernInteractionsShim`, `_FernWebhooksShim`, `_FernAgentsShim`) described in earlier versions of this document no longer exist. `client.fern_interactions` now directly returns `self._fern_nextgen_client.fern_interactions` (a `FernInteractionsClient` / `AsyncFernInteractionsClient`).

---

## 1. Per‑method breaking changes

### 1.1 `interactions`

| Method | Fern signature (`client.fern_interactions.*`) | Stainless signature (`client.interactions.*`) | Breaking? |
|---|---|---|---|
| `create` | `create(*, request: CreateFernInteractionsRequest, request_options=None)` where `CreateFernInteractionsRequest = Union[CreateModelInteractionParams, CreateAgentInteractionParams]` | `create(*, input, model \| agent, [stream, background, environment, generation_config, response_format, response_mime_type, response_modalities, service_tier, store, system_instruction, tools, webhook_config, agent_config, previous_interaction_id, api_version, extra_headers, extra_query, extra_body, timeout])` with `@required_args(["input","model"], ["input","model","stream"], ["agent","input"], ["agent","input","stream"])` | **Yes — completely different calling convention** |
| `create_stream` | `create_stream(*, request: CreateFernInteractionsStreamRequest, request_options=None) -> Iterator[InteractionSseEvent]` | **does not exist**; use `create(..., stream=True)` which returns `Stream[InteractionSSEEvent]` | **Yes — method missing on Stainless** |
| `get` | `get(id: str, *, stream, last_event_id, include_input, request_options) -> Interaction` | `get(id: str, *, include_input, last_event_id, stream, api_version, extra_*…) -> Interaction \| Stream[InteractionSSEEvent]` | No — `id` positional on both, kwargs mostly align. |
| `get_stream` | `get_stream(id: str, *, stream, last_event_id, include_input, request_options) -> Iterator[InteractionSseEvent]` | **does not exist**; use `get(id, stream=True)` returning `Stream[InteractionSSEEvent]` | **Yes — method missing on Stainless** |
| `cancel` | `cancel(id: str, *, request_options=None) -> Interaction` | `cancel(id, *, api_version, extra_*…) -> Interaction` | No. |
| `delete` | `delete(id: str, *, request_options=None) -> typing.Dict[str, Any]` | `delete(id, *, api_version, extra_*…) -> object` | No (typing‑only). |

#### Concrete consequences for calling code

```python
# Fern — pass a typed Pydantic model
from google.genai._fern_interactions.types import CreateModelInteractionParams, TextContent

client.fern_interactions.create(
    request=CreateModelInteractionParams(
        model="gemini-2.5-computer-use-preview-10-2025",
        input=TextContent(text="Hello from Fern", type="text"),
    )
)

# Stainless equivalent — loose kwargs
client.interactions.create(input="Hello from Fern", model="gemini-2.5-computer-use-preview-10-2025")

# Fern streaming
client.fern_interactions.create_stream(
    request=CreateModelInteractionParams(
        model="gemini-2.5-computer-use-preview-10-2025",
        input=TextContent(text="Hello", type="text"),
        stream=True,
    )
)
# Stainless equivalent
client.interactions.create(input="Hello", model="gemini-2.5-computer-use-preview-10-2025", stream=True)

# get_stream: Fern
client.fern_interactions.get_stream(created_id)
# Stainless equivalent
client.interactions.get(created_id, stream=True)
```

### 1.2 `webhooks`

| Method | Fern signature | Stainless signature | Breaking? |
|---|---|---|---|
| `list` | `list(*, page_size, page_token, request_options) -> ListWebhooksResponse` | `list(*, page_size, page_token, api_version, extra_*…) -> WebhookListResponse` | Class name only. |
| `create` | `create(*, subscribed_events, uri, name=OMIT, request_options) -> Webhook` | `create(*, subscribed_events, uri, name, api_version, extra_*…) -> Webhook` | No — same required fields. |
| `get` | `get(id: str, *, request_options) -> Webhook` | `get(id, *, api_version, extra_*…) -> Webhook` | No. |
| `update` | `update(id: str, *, update_mask, name, state, subscribed_events, uri, request_options) -> Webhook` | `update(id, *, update_mask, name, state, subscribed_events, uri, api_version, extra_*…) -> Webhook` | No — fields match. |
| `rotate_signing_secret` | `rotate_signing_secret(id: str, *, revocation_behavior=OMIT, request_options) -> RotateSigningSecretResponse` | `rotate_signing_secret(id, *, revocation_behavior, api_version, extra_*…) -> WebhookRotateSigningSecretResponse` | Class name only. |
| `ping` | `ping(id: str, *, request: PingWebhookRequest, request_options) -> PingWebhookResponse` | `ping(id, *, body: webhook_ping_params.Body \| Omit = omit, api_version, extra_*…) -> WebhookPingResponse` | **Yes — kwarg named `request` on Fern vs `body` on Stainless. Also required on Fern, optional on Stainless.** |
| `delete` | `delete(id: str, *, request_options) -> Empty` | `delete(id, *, api_version, extra_*…) -> WebhookDeleteResponse` | Class name only. |

#### Concrete consequence

```python
# Fern (current)
client.fern_webhooks.ping(id=webhook_id, request={})
# Stainless equivalent
client.webhooks.ping(id=webhook_id, body={})
# Calling Stainless with `request={}` raises:
#   TypeError: ping() got an unexpected keyword argument 'request'
```

### 1.3 `agents`

| Method | Fern signature | Stainless signature | Breaking? |
|---|---|---|---|
| `list` | `list(*, parent, page_size, page_token, request_options) -> ListAgentsResponse` | `list(*, page_size, page_token, parent, api_version, extra_*…) -> AgentListResponse` | Class name only. `parent` now explicit on both. |
| `create` | `create(*, id, base_agent, base_environment, description, system_instruction, tools, request_options) -> Agent` | `create(*, id, base_agent, base_environment, description, system_instruction, tools, api_version, extra_*…) -> Agent` | No — field names match 1:1. |
| `get` | `get(id: str, *, request_options) -> Agent` | `get(id, *, api_version, extra_*…) -> Agent` | No. |
| `delete` | `delete(id: str, *, request_options) -> Empty` | `delete(id, *, api_version, extra_*…) -> AgentDeleteResponse` | Class name only. |

---

## 2. Cross‑cutting differences (apply to every method)

### 2.1 `api_version`

- **Stainless**: every method accepts `api_version: str | None = None` as a keyword. If `None`, falls back to `self._client._get_api_version_path_param()`. You can override per call.
- **Fern**: `api_version` is **pre‑bound** at construction time in `_build_sync_fern_nextgen` / `_build_async_fern_nextgen` (set to `''` for Vertex, `http_opts.api_version or 'v1beta'` for Gemini). It is not exposed on individual method calls — you cannot override it per call without dropping down to `_fern_nextgen_client.fern_interactions.<m>(...)` directly and constructing the path yourself.

### 2.2 Per‑request escape hatch

| Concern | Stainless kwarg | Fern field (inside `RequestOptions`) |
|---|---|---|
| Extra headers | `extra_headers=` | `additional_headers=` |
| Extra query params | `extra_query=` | `additional_query_parameters=` |
| Extra body fields | `extra_body=` | `additional_body_parameters=` |
| Per‑call timeout | `timeout=` (`float \| httpx.Timeout \| None`) | `timeout_in_seconds=` (`int`) |
| Retries | (client‑level only) | `max_retries=` per call |

The structure differs too: Stainless takes loose kwargs on each method; Fern takes a single `request_options=RequestOptions(...)` object. **Naming is incompatible across the board.**

### 2.3 Streaming model

- **Stainless**: streaming is an overload of the same method. `create(stream=True)` returns `Stream[InteractionSSEEvent]`; `get(stream=True)` returns `Stream[InteractionSSEEvent]`. Async variants return `AsyncStream[...]`. There is also Vertex‑specific stream subclassing — `LegacyLyriaInteractionStream`, `LegacyLyriaInteractionDetectingStream` — that activates the per‑event SSE remap for legacy Lyria models.
- **Fern**: streaming is a **separate method** (`create_stream`, `get_stream`) returning `Iterator[InteractionSseEvent]` / `AsyncIterator[InteractionSseEvent]`. No Vertex Lyria stream coercion.

Also note the event‑class casing: `InteractionSSEEvent` (Stainless) vs `InteractionSseEvent` (Fern). Same JSON shape, different Python classes from different modules.

### 2.4 Required‑arg validation

- **Stainless** `interactions.create` is wrapped with `@required_args(["input","model"], ["input","model","stream"], ["agent","input"], ["agent","input","stream"])` and explicitly rejects mixing `model`+`agent_config` or `agent`+`generation_config`. These checks run client‑side before the HTTP call.
- **Fern** `fern_interactions.create` accepts `request: Union[CreateModelInteractionParams, CreateAgentInteractionParams]`. The Pydantic model (`CreateModelInteractionParams`) validates required fields (`model`, `input`) at instantiation time, so field errors surface at Python level — but there is no Fern‑side guard against mixing `model`+`agent_config`.

### 2.5 `with_raw_response` / `with_streaming_response`

- **Stainless**: every resource exposes both `with_raw_response` (a `*WithRawResponse` wrapper) and `with_streaming_response` (a `*WithStreamingResponse` wrapper) as `cached_property`.
- **Fern**: exposes only `with_raw_response`. There is no `with_streaming_response`.

### 2.6 Return‑type identity

Every response model lives in a different module:

| Concept | Stainless class | Fern class |
|---|---|---|
| Interaction | `google.genai._interactions.types.interaction.Interaction` | `google.genai._fern_interactions.types.interaction.Interaction` |
| Interaction SSE event | `InteractionSSEEvent` | `InteractionSseEvent` |
| Webhook | `_interactions.types.webhook.Webhook` | `_fern_interactions.types.webhook.Webhook` |
| Webhook list | `WebhookListResponse` | `ListWebhooksResponse` |
| Webhook delete | `WebhookDeleteResponse` | `Empty` |
| Webhook ping | `WebhookPingResponse` | `PingWebhookResponse` |
| Webhook rotate secret | `WebhookRotateSigningSecretResponse` | `RotateSigningSecretResponse` |
| Agent | `_interactions.types.agent.Agent` | `_fern_interactions.types.agent.Agent` |
| Agent list | `AgentListResponse` | `ListAgentsResponse` |
| Agent delete | `AgentDeleteResponse` | `Empty` |

Same JSON shape, **different Python classes**. Code that does `isinstance(x, Webhook)`, imports the model for type hints, or depends on `model_dump`/`model_dump_json` (Stainless) vs `.json()` / `.dict()` (Fern Pydantic) semantics will break on swap.

### 2.7 `id` parameter binding

Both Fern and Stainless now expose `id` as **positional‑or‑keyword** (`def get(self, id: str, *, …)`). This was a breaking difference in earlier versions but is no longer the case. Positional or keyword calls work on both surfaces.

### 2.8 Vertex path/routing differences

- **Stainless**: `_build_maybe_vertex_path(api_version=…, path=…)` handles the `projects/{project}/locations/{location}` prefix automatically, and the `LegacyLyriaInteractionStream` / `LegacyLyriaInteractionDetectingStream` classes rewrite legacy Lyria SSE events for Vertex. Detection is driven by `self._client._is_vertex` and `is_legacy_lyria_request(...)`.
- **Fern**: no equivalent legacy‑Lyria coercion path. Vertex base URL has the version embedded so the wrapper `api_version` is set to `''`; callers can't override this per request.

---

## 3. Summary cheat‑sheet (Fern → Stainless)

```python
# 1) create — Fern uses a typed Pydantic request object
#    Fern:
from google.genai._fern_interactions.types import CreateModelInteractionParams, TextContent
client.fern_interactions.create(
    request=CreateModelInteractionParams(
        model="gemini-2.5-computer-use-preview-10-2025",
        input=TextContent(text="Hello", type="text"),
    )
)
#    Stainless:
client.interactions.create(input="Hello", model="gemini-2.5-computer-use-preview-10-2025")

# 2) create_stream  (method does not exist on Stainless)
stream = client.interactions.create(input="Hello", model="gemini-2.5-computer-use-preview-10-2025", stream=True)
for chunk in stream: ...

# 3) get
client.interactions.get(created_id)

# 4) get_stream  (method does not exist on Stainless)
stream = client.interactions.get(created_id, stream=True)
for chunk in stream: ...

# 5) cancel / delete  — identical shape
client.interactions.cancel(created_id)
client.interactions.delete(created_id)

# 6) webhooks.list / create / get / update / delete / rotate_signing_secret  — identical shape (class names differ)
client.webhooks.list()
client.webhooks.create(uri="https://example.com/hook", subscribed_events=["interaction.completed"])
client.webhooks.get(webhook_id)
client.webhooks.update(webhook_id, state="enabled")
client.webhooks.rotate_signing_secret(webhook_id)
client.webhooks.delete(webhook_id)

# 7) webhooks.ping  — kwarg renamed
client.webhooks.ping(webhook_id, body={})        # Stainless
# client.webhooks.ping(webhook_id, request={})   # would TypeError on Stainless

# 8) agents.list / create / get / delete  — identical shape (class names differ)
vertex_client.agents.list()
vertex_client.agents.create(id="poc-agent", system_instruction="You are a helpful assistant.")
vertex_client.agents.get(agent_id)
vertex_client.agents.delete(agent_id)
```

## 4. Hard breaks (a literal swap will fail)

1. **`fern_interactions.create_stream`** — no Stainless equivalent; rewrite as `create(..., stream=True)`.
2. **`fern_interactions.get_stream`** — no Stainless equivalent; rewrite as `get(id, stream=True)`.
3. **`fern_interactions.create(request=CreateModelInteractionParams(...))`** — Stainless has no `request` kwarg; rewrite to loose typed kwargs (`input`, `model`, …) and `extra_body=` for unmodeled fields.
4. **`fern_webhooks.ping(request=...)`** — Stainless uses `body=` (and the body is optional, not required).
5. **`RequestOptions` field names** — `additional_headers / additional_query_parameters / additional_body_parameters / timeout_in_seconds / max_retries` must be translated to `extra_headers / extra_query / extra_body / timeout` (and `max_retries` is client‑level only on Stainless).
6. **`with_streaming_response`** — only exists on Stainless. Code that relies on it can't be written against `client.fern_*`.
7. **Return‑type imports** — any `from google.genai._interactions.types.* import ...` (or vice versa) is module‑specific. Swapping providers requires changing every import and every `isinstance` check.

## 5. Soft breaks (code runs, behavior differs)

1. **Pre‑bound `api_version`** on Fern: callers can't override per request.
2. **Vertex Lyria SSE remap** is Stainless‑only.
3. **Client‑side required‑arg mutual‑exclusion validation** (`model`+`agent_config` guard) is Stainless‑only — Fern lets you construct an invalid request that the server then rejects.
4. **`delete` return type**: Stainless returns `object` / `WebhookDeleteResponse` / `AgentDeleteResponse`; Fern returns `typing.Dict[str, Any]` / `Empty`.
