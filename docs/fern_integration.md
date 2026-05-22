# Fern integration: custom auth + Vertex path routing

This doc explains how two pieces of custom functionality landed for the existing Stainless `_interactions/` SDK are mirrored for the new Fern `_fern_interactions/` SDK in `google/genai/client.py`.

The Stainless and Fern paths share the same `BaseApiClient` (API key / OAuth credentials / project / location) but each SDK has its own seam for plugging dynamic auth and Vertex URL routing in. The behaviour on the wire is identical.

---

## 1. Per-request auth injection

### Stainless seam

`_interactions/_client_adapter.py` defines abstract `GeminiNextGenAPIClientAdapter` / `AsyncGeminiNextGenAPIClientAdapter` with:

- `is_vertex_ai()`
- `get_project()`
- `get_location()`
- `get_auth_headers()` / `async_get_auth_headers()`

The concrete subclass passed into `GeminiNextGenAPIClient(client_adapter=...)` lives in `client.py`. The Stainless SDK's `_prepare_options` override calls `client_adapter.get_auth_headers()` per request, merging the result into the outgoing `options.headers`.

### Fern seam

Fern's `SyncClientWrapper` / `AsyncClientWrapper` pass their own `get_headers` (sync) and `async_get_headers` (async) as **callables** to the underlying `HttpClient` — the callable is invoked **per request** to produce the header dict.

We subclass both wrappers and override those callables:

```python
# google/genai/client.py
class _FernGenAiSyncClientWrapper(_FernSyncWrapper):
  def __init__(self, *, api_client: BaseApiClient, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._api_client = api_client

  def get_headers(self) -> dict[str, str]:
    headers = super().get_headers()
    if self._api_client.api_key:
      headers['x-goog-api-key'] = self._api_client.api_key
      return headers
    headers.pop('x-goog-api-key', None)
    token = self._api_client._access_token()
    headers['Authorization'] = f'Bearer {token}'
    if (creds := self._api_client._credentials) and creds.quota_project_id:
      headers['x-goog-user-project'] = creds.quota_project_id
    return headers


class _FernGenAiAsyncClientWrapper(_FernAsyncWrapper):
  async def async_get_headers(self) -> dict[str, str]:
    headers = self.get_headers()
    if not self._api_client.api_key:
      token = await self._api_client._async_access_token()
      headers['Authorization'] = f'Bearer {token}'
      if (creds := self._api_client._credentials) and creds.quota_project_id:
        headers['x-goog-user-project'] = creds.quota_project_id
    return headers
```

Fern's `GeminiNextGenAPIClient.__init__` always builds its own `SyncClientWrapper` first. We immediately swap it for our subclass and clear the lazily-built resource caches so the new wrapper takes effect:

```python
# _build_sync_fern_nextgen, client.py
nextgen = _FernSyncClient(base_url=..., api_key=api_key, api_version=wrapper_api_version, ...)
nextgen._client_wrapper = _FernGenAiSyncClientWrapper(
    api_client=api_client,
    base_url=base_url,
    api_version=wrapper_api_version,
    api_key=api_key,
    headers=http_opts.headers,
    httpx_client=api_client._httpx_client,
    ...
)
nextgen._fern_interactions = None
nextgen._fern_webhooks = None
nextgen._fern_agents = None
```

### API-key placeholder

Fern's `GeminiNextGenAPIClient.__init__` raises if `api_key is None`. When running on Vertex we pass the sentinel string `"vertex-oauth"`. Our `get_headers()` override pops `x-goog-api-key` from the base headers before adding the Bearer token, so the placeholder never reaches the wire.

### Behaviour parity

| Concern | Result |
|---|---|
| Gemini sends `x-goog-api-key` | yes (`test_fern_auth.py::test_fern_interactions_gemini_url`) |
| Vertex sends `Authorization: Bearer <token>` | yes (`test_fern_interactions_vertex_auth_header`) |
| Vertex sends `x-goog-user-project` when creds carry quota | yes |
| Token refresh per retry | yes (`test_fern_interactions_vertex_auth_refresh_on_retry`) — `_access_token()` invoked on every call |
| Gemini path skips OAuth fetch | yes (`test_fern_interactions_gemini_no_vertex_auth`) — `_access_token()` never called |

---

## 2. Vertex path routing

### Stainless seam

`_interactions/_base_client.py:418` — `_build_maybe_vertex_path` is called **per request** by every resource method:

```python
def _build_maybe_vertex_path(self, *, api_version: str, path: str) -> str:
    if not self._is_vertex or not self._vertex_location or not self._vertex_project:
        return f'/{api_version}/{path}'
    return f'{api_version}/projects/{self._vertex_project}/locations/{self._vertex_location}/{path}'
```

The base_url stays at `https://{location}-aiplatform.googleapis.com/`, the per-call path embeds project + location.

### Fern seam

Fern's generated raw clients now interpolate a **single** version segment from the wrapper:

```python
# _fern_interactions/fern_interactions/raw_client.py
self._client_wrapper.httpx_client.request(
    f"{encode_path_param(self._client_wrapper._api_version)}/interactions",
    method="POST",
    ...
)
```

`encode_path_param` does not URL-encode slashes — `str(jsonable_encoder(obj))`. That means whatever we put in `wrapper._api_version` lands in the path verbatim, and the resource methods (`create`, `get`, `cancel`, etc.) take no `api_version` argument at all.

Workaround: for Vertex we augment `base_url` with `/{version}/projects/{p}/locations/{l}` at construction time and leave `wrapper._api_version` empty. For Gemini we keep `base_url` at the host root and put the version in `wrapper._api_version`. Either way the wire URL ends up correct without any per-call boilerplate.

```python
# client.py
def _fern_base_url(api_client: BaseApiClient) -> str:
  http_opts = api_client._http_options
  if api_client.vertexai:
    # User already supplied a fully-formed URL with project/location -> trust as-is.
    if http_opts.base_url and '/projects/' in http_opts.base_url:
      return http_opts.base_url.rstrip('/')
    # Trust the host BaseApiClient already picked (handles global,
    # multi-regional, api_key+vertex, custom base_url). Append the
    # project/location path Fern's per-call template will be joined onto.
    host = (http_opts.base_url or f'https://{api_client.location}-aiplatform.googleapis.com').rstrip('/')
    version = http_opts.api_version or 'v1beta1'
    return f'{host}/{version}/projects/{api_client.project}/locations/{api_client.location}'
  if http_opts.base_url:
    return _VERSION_SUFFIX.sub('', http_opts.base_url).rstrip('/')
  return 'https://generativelanguage.googleapis.com'
```

```python
# _build_sync_fern_nextgen, client.py
wrapper_api_version = '' if api_client.vertexai else (http_opts.api_version or 'v1beta')
```

### Why the wrapper api_version is empty for Vertex

If we left `wrapper._api_version = "v1beta1"` for Vertex, the version would appear twice in the URL:

```
https://us-central1-aiplatform.googleapis.com/v1beta1/projects/p/locations/us-central1/v1beta1/interactions
                                              ^^^^^^^                                   ^^^^^^^
                                            in base_url                              re-added by Fern
```

Empty wrapper api_version makes Fern interpolate an empty string into the path template:

```python
f"{encode_path_param('')}/interactions"     # -> "/interactions"
```

`_build_url` then joins that against the pre-augmented Vertex base_url with a single `/`.

### Final URLs on the wire

| Surface | base_url | wrapper.api_version | path interpolation | wire URL |
|---|---|---|---|---|
| Gemini | `https://generativelanguage.googleapis.com` | `v1beta` | `v1beta/interactions` | `https://generativelanguage.googleapis.com/v1beta/interactions` |
| Vertex | `https://us-central1-aiplatform.googleapis.com/v1beta1/projects/<p>/locations/us-central1` | `""` | `/interactions` | `https://us-central1-aiplatform.googleapis.com/v1beta1/projects/<p>/locations/us-central1/interactions` |
| Vertex `global` | `https://aiplatform.googleapis.com/v1beta1/projects/<p>/locations/global` | `""` | `/interactions` | `https://aiplatform.googleapis.com/v1beta1/projects/<p>/locations/global/interactions` |

Identical to what Stainless produces via `_build_maybe_vertex_path`.

Verified by:
- `test_fern_paths.py` — sync + async URL assertions
- `test_fern_auth.py::test_fern_interactions_vertex_url`
- `ete-test.py` live run against both Gemini and Vertex global

---

## Tradeoffs

| | Stainless | Fern |
|---|---|---|
| Auth seam | adapter passed to constructor; `_prepare_options` hook called per-request | `*ClientWrapper` subclass; `get_headers` / `async_get_headers` callbacks invoked per-request |
| Path routing seam | per-request `_build_maybe_vertex_path` | construction-time `_fern_base_url` augments base_url; `wrapper._api_version` interpolated per request by Fern codegen |
| User-supplied `base_url` override on Vertex | trusted as-is | trusted only when it contains `/projects/` (otherwise treated as host root and augmented) |
| Adapter introspection (`is_vertex_ai`, `get_project`, `get_location`) | yes, abstract interface | not exposed — wrapper holds `BaseApiClient` directly |
| Token refresh on retry | yes | yes |
| Resource methods take `api_version` arg | yes (passed as `api_version=`) | no — codegen baked into wrapper |
| Shim layer in `client.py` | none | none (resource clients exposed directly via `Client.fern_interactions` / `fern_webhooks` / `fern_agents`) |

Functionally equivalent for the POC. Stainless's per-request hooks are more flexible if project/location ever need to vary per request; Fern's per-client baking keeps the hot path simpler. Today neither matters.

`_fern_base_url` could be eliminated by stuffing `{version}/projects/.../locations/...` straight into `wrapper._api_version` (slashes pass through `encode_path_param` unchanged). Today the function still exists for clarity; refactor is tracked but not blocking.
