# Breaking changes: `client.fern_*` (Fern) vs `client.<x>` (Stainless `_interactions`)

This document enumerates the interface deltas between the **Fern‑generated** surface (exposed on `genai.Client` as `client.fern_interactions`, `client.fern_webhooks`, `client.fern_agents` via the shims in `google/genai/client.py`) and the **Stainless‑generated** surface (exposed as `client.interactions`, `client.webhooks`, `client.agents` and implemented under `google/genai/_interactions/`).

Source files compared:

- Fern client methods: `google/genai/_fern_interactions/fern_interactions/client.py`, `google/genai/_fern_interactions/fern_webhooks/client.py`, `google/genai/_fern_interactions/fern_agents/client.py`
- Fern shim wrappers: `google/genai/client.py` (`_FernInteractionsShim`, `_FernWebhooksShim`, `_FernAgentsShim` and their async siblings)
- Stainless resources: `google/genai/_interactions/resources/{interactions,webhooks,agents}.py`
- POC exercising the Fern surface: `simple_fern_test.py`

The comparison is intentionally framed as "if I swap `client.fern_X` for `client.X`, what breaks?"

---

## 1. Per‑method breaking changes

### 1.1 `interactions`

| Method | Fern shim signature (`client.fern_interactions.*`) | Stainless signature (`client.interactions.*`) | Breaking? |
|---|---|---|---|
| `create` | `create(*, request_options: RequestOptions \| None = None)` | `create(*, input, model \| agent, [stream, background, environment, generation_config, response_format, response_mime_type, response_modalities, service_tier, store, system_instruction, tools, webhook_config, agent_config, previous_interaction_id, api_version, extra_headers, extra_query, extra_body, timeout])` with `@required_args(["input","model"], ["input","model","stream"], ["agent","input"], ["agent","input","stream"])` | **Yes** |
| `create_stream` | `create_stream(*, request_options=None) -> Iterator[InteractionSseEvent]` | **does not exist**; use `create(..., stream=True)` which returns `Stream[InteractionSSEEvent]` | **Yes — method missing on Stainless** |
| `get` | `get(*, id: str, request_options=None, **kwargs) -> Interaction` | `get(id: str, *, include_input, last_event_id, stream, api_version, extra_*…) -> Interaction \| Stream[InteractionSSEEvent]` | Mostly no. Fern shim makes `id` **keyword‑only**; Stainless allows positional. POC uses `id=`, so it survives. |
| `get_stream` | `get_stream(*, id, request_options=None, **kwargs) -> Iterator[InteractionSseEvent]` | **does not exist**; use `get(id, stream=True)` returning `Stream[InteractionSSEEvent]` | **Yes — method missing on Stainless** |
| `cancel` | `cancel(*, id, request_options=None) -> Interaction` | `cancel(id, *, api_version, extra_*…) -> Interaction` | No (id‑positional difference only). |
| `delete` | `delete(*, id, request_options=None) -> typing.Dict[str, Any]` | `delete(id, *, api_version, extra_*…) -> object` | No (typing‑only). |

#### Concrete consequences for `simple_fern_test.py`

```python
# Fern (current)
client.fern_interactions.create(
    request_options=RequestOptions(additional_body_parameters={"model": "gemini-3.5-flash", "input": "Hello from Fern POC"})
)
# Stainless equivalent
client.interactions.create(input="Hello from Fern POC", model="gemini-3.5-flash")

# Fern (current)
client.fern_interactions.create_stream(
    request_options=RequestOptions(additional_body_parameters={"model": "gemini-3.5-flash", "input": "Hello", "stream": True})
)
# Stainless equivalent
client.interactions.create(input="Hello", model="gemini-3.5-flash", stream=True)

# Fern (current)
client.fern_interactions.get_stream(id=created_id, stream=True)
# Stainless equivalent
client.interactions.get(id=created_id, stream=True)
```

### 1.2 `webhooks`

| Method | Fern shim | Stainless | Breaking? |
|---|---|---|---|
| `list` | `list(**kwargs) -> ListWebhooksResponse` | `list(*, page_size, page_token, api_version, extra_*…) -> WebhookListResponse` | Class name only. |
| `create` | `create(**kwargs) -> Webhook` — extra optional fields: `create_time, id, signing_secrets, state, update_time, new_signing_secret` | `create(*, subscribed_events, uri, name, api_version, extra_*…) -> Webhook` | Fern accepts a wider set of optional fields. Common fields (`uri`, `subscribed_events`, `name`) line up. |
| `get` | `get(*, id, **kwargs) -> Webhook` | `get(id, *, api_version, extra_*…) -> Webhook` | id‑positional only. |
| `update` | `update(*, id, **kwargs) -> Webhook` | `update(id, *, update_mask, name, state, subscribed_events, uri, api_version, extra_*…) -> Webhook` | id‑positional only. |
| `rotate_signing_secret` | `rotate_signing_secret(*, id, **kwargs) -> RotateSigningSecretResponse` | `rotate_signing_secret(id, *, revocation_behavior, api_version, extra_*…) -> WebhookRotateSigningSecretResponse` | Class name only. |
| `ping` | `ping(*, id, **kwargs)` then forwarded to `ping(api_version, id, *, request: PingWebhookRequest, …) -> PingWebhookResponse` | `ping(id, *, body: webhook_ping_params.Body \| Omit = omit, api_version, extra_*…) -> WebhookPingResponse` | **Yes — kwarg renamed `request` → `body`, and required → optional.** |
| `delete` | `delete(*, id, **kwargs) -> Empty` | `delete(id, *, api_version, extra_*…) -> WebhookDeleteResponse` | Class name only. |

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

| Method | Fern shim | Stainless | Breaking? |
|---|---|---|---|
| `list` | `list(**kwargs) -> ListAgentsResponse` | `list(*, page_size, page_token, parent, api_version, extra_*…) -> AgentListResponse` | Class name only. |
| `create` | `create(**kwargs) -> Agent` | `create(*, id, base_agent, base_environment, description, system_instruction, tools, api_version, extra_*…) -> Agent` | No — field names match 1:1. |
| `get` | `get(*, id, **kwargs) -> Agent` | `get(id, *, api_version, extra_*…) -> Agent` | id‑positional only. |
| `delete` | `delete(*, id, **kwargs) -> Empty` | `delete(id, *, api_version, extra_*…) -> AgentDeleteResponse` | Class name only. |

---

## 2. Cross‑cutting differences (apply to every method)

### 2.1 `api_version`

- **Stainless**: every method accepts `api_version: str | None = None` as a keyword. If `None`, falls back to `self._client._get_api_version_path_param()`. You can override per call.
- **Fern shim**: `api_version` is **pre‑bound** in `_FernInteractionsShim.__init__` / `_FernWebhooksShim.__init__` / `_FernAgentsShim.__init__`. The shim *removes* `api_version` from the user‑facing signature entirely — you cannot override it per call without dropping down to `_fern_nextgen_client.fern_interactions.<m>(api_version, …)` directly.

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
- **Fern** `fern_interactions.create` takes no body kwargs at all — the body must be supplied via `request_options.additional_body_parameters`. Missing fields surface only as server‑side errors.

### 2.5 `with_raw_response` / `with_streaming_response`

- **Stainless**: every resource exposes both `with_raw_response` (a `*WithRawResponse` wrapper) and `with_streaming_response` (a `*WithStreamingResponse` wrapper) as `cached_property`.
- **Fern shim**: exposes only `with_raw_response`. There is no `with_streaming_response`.

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

Same JSON shape, **different Python classes**. Code that does `isinstance(x, Webhook)`, imports the model for type hints, or depends on `model_dump`/`model_dump_json` (Stainless) vs `.json()` / `.dict()` (Fern) semantics will break on swap.

### 2.7 `id` parameter binding

Across the Fern shim, `id` is **keyword‑only** (`def get(self, *, id: str, ...)`). On Stainless it is positional‑or‑keyword (`def get(self, id: str, *, …)`).

- Fern → Stainless: positional call works, keyword call works.
- Stainless → Fern: keyword call works, **positional call breaks** (`client.fern_webhooks.get(webhook_id)` would raise `TypeError: get() takes 1 positional argument but 2 were given`).

### 2.8 Vertex path/routing differences

- **Stainless**: `_build_maybe_vertex_path(api_version=…, path=…)` handles the `projects/{project}/locations/{location}` prefix automatically, and the `LegacyLyriaInteractionStream` / `LegacyLyriaInteractionDetectingStream` classes rewrite legacy Lyria SSE events for Vertex. Detection is driven by `self._client._is_vertex` and `is_legacy_lyria_request(...)`.
- **Fern**: no equivalent legacy‑Lyria coercion path. `_FernAgentsShim` on Vertex relies on whatever path the Fern client emits.

---

## 3. Summary cheat‑sheet (Fern → Stainless)

For each call in `simple_fern_test.py`, here is the minimum edit needed to run against the Stainless surface:

```python
# 1) create
client.interactions.create(input="Hello from Fern POC", model="gemini-3.5-flash")

# 2) create_stream  (method does not exist on Stainless)
stream = client.interactions.create(input="Hello", model="gemini-3.5-flash", stream=True)
for chunk in stream: ...

# 3) get
client.interactions.get(id=created_id)

# 4) get_stream  (method does not exist on Stainless)
stream = client.interactions.get(id=created_id, stream=True)
for chunk in stream: ...

# 5) cancel / delete  — identical shape
client.interactions.cancel(id=created_id)
client.interactions.delete(id=created_id)

# 6) webhooks.list / create / get / update / delete / rotate_signing_secret  — identical shape (class names differ)
client.webhooks.list()
client.webhooks.create(uri="https://example.com/hook", subscribed_events=["interaction.completed"])
client.webhooks.get(id=webhook_id)
client.webhooks.update(id=webhook_id, state="enabled")
client.webhooks.rotate_signing_secret(id=webhook_id)
client.webhooks.delete(id=webhook_id)

# 7) webhooks.ping  — kwarg renamed
client.webhooks.ping(id=webhook_id, body={})        # Stainless
# client.webhooks.ping(id=webhook_id, request={})   # would TypeError

# 8) agents.list / create / get / delete  — identical shape (class names differ)
vertex_client.agents.list()
vertex_client.agents.create(id="poc-agent", system_instruction="You are a helpful assistant.")
vertex_client.agents.get(id=agent_id)
vertex_client.agents.delete(id=agent_id)
```

## 4. Hard breaks (a literal swap will fail)

1. **`fern_interactions.create_stream`** — no Stainless equivalent; rewrite as `create(..., stream=True)`.
2. **`fern_interactions.get_stream`** — no Stainless equivalent; rewrite as `get(id=..., stream=True)`.
3. **`fern_interactions.create(request_options=RequestOptions(additional_body_parameters=...))`** — Stainless has no `request_options`; rewrite to typed kwargs (`input`, `model`, …) and `extra_body=` for unmodeled fields.
4. **`fern_webhooks.ping(request=...)`** — Stainless uses `body=` (and the body is optional, not required).
5. **`RequestOptions` field names** — `additional_headers / additional_query_parameters / additional_body_parameters / timeout_in_seconds / max_retries` must be translated to `extra_headers / extra_query / extra_body / timeout` (and `max_retries` is client‑level only on Stainless).
6. **`with_streaming_response`** — only exists on Stainless. Code that relies on it can't be written against `client.fern_*`.
7. **Return‑type imports** — any `from google.genai._interactions.types.* import ...` (or vice versa) is module‑specific. Swapping providers requires changing every import and every `isinstance` check.

## 5. Soft breaks (code runs, behavior differs)

1. **Pre‑bound `api_version`** on Fern: callers can't override per request.
2. **Vertex Lyria SSE remap** is Stainless‑only.
3. **Client‑side required‑arg validation** (`@required_args`) is Stainless‑only — Fern will let you POST an empty body and let the server reject it.
4. **`delete` return type**: Stainless returns `object` / `WebhookDeleteResponse` / `AgentDeleteResponse`; Fern returns `typing.Dict[str, Any]` / `Empty`.
5. **`webhooks.create`** accepts a strictly wider set of optional fields on Fern (`create_time`, `id`, `signing_secrets`, `state`, `update_time`, `new_signing_secret`). Stainless will reject these as unknown kwargs (though they could be passed via `extra_body`).
