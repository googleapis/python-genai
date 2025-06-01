# Report 1: Endpoint Connection

This report details how the SDK establishes a connection with the live audio endpoint.

## 0. Required Packages

For basic WebSocket connection and SDK functionality, the primary packages are:

-   `google-generativeai`: The core SDK. This includes the `websockets` library as a dependency.
-   `asyncio`: For running the asynchronous operations (built-in Python library).
-   `google-auth`: (Often a dependency of `google-cloud-aiplatform` or used directly) for authentication, especially when using Vertex AI with Application Default Credentials.

Specific examples might require additional packages for tasks like handling API keys from environment variables (e.g., `python-dotenv`).

## 1. Connection Mechanism

The SDK primarily uses **WebSockets** for real-time communication with the live audio endpoint. The `websockets` Python library is leveraged for this purpose.

- The connection process is initiated within the `AsyncLive.connect` method (in `google/genai/live.py`).
- It utilizes `websockets.asyncio.client.connect` (or `websockets.client.connect` for older versions of the library) to establish the asynchronous WebSocket connection.

## 2. URI Construction

The WebSocket URI is dynamically constructed based on the client configuration (Google AI vs. Vertex AI) and API details.

- **Base URL**:
    - The WebSocket base URL is derived from `self._api_client._websocket_base_url()`.
    - This method typically takes the HTTP base URL (e.g., `https://aiplatform.googleapis.com/` for Vertex AI, or `https://generativelanguage.googleapis.com/` for Google AI) and changes the scheme from `http/https` to `wss`.

- **Path and Query Parameters**:

    -   **Google AI (genai) - General Content:**
        ```
        wss://{base_url}/ws/google.ai.generativelanguage.{version}.GenerativeService.{method}?{key_name}={api_key}
        ```
        -   `{version}`: API version (e.g., `v1beta`).
        -   `{method}`: Can be `BidiGenerateContent` or `BidiGenerateContentConstrained`. The latter is used if the API key is an ephemeral token (`auth_tokens/...`).
        -   `{key_name}`: Is `key` for standard API keys or `access_token` for ephemeral tokens.
        -   `{api_key}`: The user's Google AI API key.

    -   **Vertex AI - General Content:**
        ```
        wss://{base_url}/ws/google.cloud.aiplatform.{version}.LlmBidiService/BidiGenerateContent
        ```
        -   `{version}`: API version (e.g., `v1beta1`).
        -   If using an API key ("express mode"), the key is sent via headers, not the URI.
        -   If using ADC/service account credentials, authentication is done via headers.

    -   **Google AI (genai) - Live Music:**
        ```
        wss://{base_url}/ws/google.ai.generativelanguage.{version}.GenerativeService.BidiGenerateMusic?key={api_key}
        ```
        -   Similar to general content for Google AI, but with a specific `BidiGenerateMusic` method.

## 3. Authentication and Headers

Authentication methods and headers vary:

-   **Google AI (genai):**
    -   The API key (`self._api_client.api_key`) is the primary authentication token, passed as a query parameter in the WebSocket URI.
    -   Standard headers defined in `self._api_client._http_options.headers` (e.g., `Content-Type`) are also sent.

-   **Vertex AI (with API Key - "express mode"):**
    -   The API key is included in the request headers (specifically `x-goog-api-key`).

-   **Vertex AI (with Application Default Credentials - ADC / Service Account):**
    -   If no explicit credentials are provided to the client, the SDK attempts to load ADC using `google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])`.
    -   A bearer token obtained from these credentials (`creds.token`) is added to the `Authorization` header (e.g., `Authorization: Bearer <token>`).
    -   If the credentials have a `quota_project_id`, it's sent in the `x-goog-user-project` header.

-   **Common Headers (All Configurations):**
    -   `user-agent`: Includes library version (e.g., `google-genai-sdk/x.y.z`) and Python version (e.g., `gl-python/a.b.c`). This is appended by `_append_library_version_headers` in `google/genai/_api_client.py`.
    -   `x-goog-api-client`: Also includes library and Python versions, and potentially an MCP usage label.
    -   If MCP (Media Control Protocol) tools are detected (via `_mcp_utils.has_mcp_tool_usage`), the `x-goog-api-client` header is augmented with `mcp_used/{mcp_version}` by `_mcp_utils.set_mcp_usage_header` (in `google/genai/_mcp_utils.py`).

## 4. Initial Handshake (Setup Request)

Once the WebSocket connection is established, an initial JSON-formatted request message is sent to the server to configure the session.

-   **Sending the Request:**
    -   `await ws.send(request)` is called within `AsyncLive.connect`.

-   **Request Payload Construction:**
    -   The content of this initial request is constructed based on whether the target is Google AI or Vertex AI, utilizing converters from `google/genai/_live_converters.py`:
        -   `_LiveConnectParameters_to_mldev` for Google AI.
        -   `_LiveConnectParameters_to_vertex` for Vertex AI.
    -   The core structure of this JSON request typically involves a `setup` object.
    -   The `setup` object contains:
        -   `model`: The name or path of the generative model to be used. The SDK's `google.genai._transformers.t_model` function transforms the user-provided model string into the fully qualified name expected by the backend.
            -   **For Google AI (genai):**
                -   User input: `'gemini-2.0-flash-live-001'` might be transformed to `'models/gemini-2.0-flash-live-001'`.
                -   The initial JSON request payload sent over WebSocket would look like:
                    ```json
                    {
                      "setup": {
                        "model": "models/gemini-2.0-flash-live-001",
                        "config": { // ... other config like responseModalities ...
                        }
                      }
                      // ... other setup parameters like systemInstruction, tools ...
                    }
                    ```
            -   **For Vertex AI:**
                -   User input: `'gemini-2.0-flash-live-preview-04-09'` might be transformed by `t_model` into something like `'publishers/google/models/gemini-2.0-flash-live-preview-04-09'`.
                -   This is then further prefixed with project and location by `AsyncLive.connect` if not already present, e.g., `'projects/my-project/locations/us-central1/publishers/google/models/gemini-2.0-flash-live-preview-04-09'`.
                -   The initial JSON request payload sent over WebSocket would look like:
                    ```json
                    {
                      "setup": {
                        "model": "projects/my-project/locations/us-central1/publishers/google/models/gemini-2.0-flash-live-preview-04-09",
                        "config": { // ... other config like responseModalities ...
                        }
                      }
                      // ... other setup parameters like systemInstruction, tools ...
                    }
                    ```
        -   `config`: A configuration object (`types.LiveConnectConfig`) detailing session parameters. This is processed by `_t_live_connect_config` (in `google/genai/live.py`) before conversion. This function handles:
            -   Transformation of `system_instruction`.
            -   Conversion of any MCP-defined tools (`mcp.Tool` or `mcp.ClientSession`) into the Gemini tool format using `McpToGenAiToolAdapter` or `mcp_to_gemini_tool`.
            -   The `config` can include:
                -   `generationConfig`: Parameters like `temperature`, `topP`, `topK`, `maxOutputTokens`, `responseModalities` (e.g., `["TEXT"]`, `["AUDIO"]`).
                -   `speechConfig`: For audio output, including voice selection.
                -   `systemInstruction`: Initial instructions for the model.
                -   `tools`: Definitions of available tools (functions) for the model.
                -   `sessionResumption`: Configuration for resuming previous sessions.
                -   `realtimeInputConfig`: Settings for how real-time input (like audio VAD) is handled.
                -   And other specific configurations.

-   **Receiving Initial Server Response:**
    -   After sending the setup request, the client waits for a response from the server: `await ws.recv(...)`.
    -   This initial server message is typically logged and confirms that the session setup has been acknowledged or completed by the server.

This sequence establishes the bi-directional communication channel and prepares the session for subsequent interactions.
