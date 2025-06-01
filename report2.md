# Report 2: Session Maintenance

This report outlines how the SDK maintains a session with the live audio endpoint after the initial connection is established.

## 1. WebSocket Protocol

- **Persistent Connections:** WebSockets, by their nature, provide persistent, bi-directional communication channels. Once the initial handshake (detailed in Report 1) is successful, the TCP connection underlying the WebSocket remains open.
- **Underlying Keep-Alives:** The `websockets` library, used by the SDK, typically handles standard TCP keep-alives and may also manage WebSocket-level ping/pong frames automatically to prevent intermediaries (like firewalls or load balancers) from closing the connection due to inactivity. The SDK's application layer code in `google/genai/live.py` does not appear to implement its own custom ping/pong mechanism.

## 2. Continuous Reception and Connection Monitoring

- **`AsyncSession.receive()` Loop:** The `AsyncSession.receive()` method (and its internal helper `_receive()`) continuously attempts to read data from the WebSocket using `await self._ws.recv()`.
- **Detection of Disconnection:** This constant polling for messages inherently monitors the health of the connection. If the connection is dropped by the server or an intermediary, the `_ws.recv()` call will typically raise an exception (e.g., `websockets.ConnectionClosed`). The SDK relies on this to detect session termination.

## 3. Server-Initiated Session Termination

- **`LiveServerGoAway` Message:** The SDK defines a `LiveServerGoAway` message type (see `google/genai/types.py` and its usage in `google/genai/_live_converters.py`).
    - This message allows the server to gracefully signal its intent to close the session.
    - It can include a `time_left` field, indicating how long before the session will be terminated.
- The client SDK does not have explicit logic to prevent or counteract a `LiveServerGoAway` message; it's a server directive.

## 4. Session State Resumption (Indirect Maintenance)

While not strictly about maintaining a single active WebSocket connection, the SDK has provisions for maintaining *session state* across different connections using handles:

- **`SessionResumptionConfig`:**
    - During the initial connection setup (`AsyncLive.connect`), the `config` parameter (`types.LiveConnectConfig`) can include a `session_resumption` field.
    - This field takes a `types.SessionResumptionConfig` object, which can specify a `handle` (a string identifier for a previous session) and a `transparent` flag (for Vertex AI).
    - This allows a new connection to attempt to resume a prior session's state.
    - **Example (SDK call):**
      ```python
      # Assuming 'previous_session_handle' was obtained from a LiveServerSessionResumptionUpdate
      # or a previous session that was resumable.
      config = types.LiveConnectConfig(
          session_resumption=types.SessionResumptionConfig(
              handle="previous_session_handle_string_12345",
              transparent=True # For Vertex AI, if applicable
          ),
          # ... other config like response_modalities ...
      )
      async with client.aio.live.connect(model=MODEL_NAME, config=config) as session:
          # ... session interactions ...
          pass
      ```
    - **Corresponding initial JSON handshake payload snippet (simplified):**
      When `_LiveConnectParameters_to_mldev` or `_LiveConnectParameters_to_vertex` processes this, it would include a structure similar to:
      ```json
      {
        "setup": {
          "model": "models/gemini-2.0-flash-live-001", // or Vertex equivalent
          "sessionResumption": { // Field name in the actual JSON might vary slightly (e.g. sessionResumption)
            "handle": "previous_session_handle_string_12345",
            "transparent": true // For Vertex AI
          }
          // ... other config parameters ...
        }
        // ... other top-level setup fields ...
      }
      ```

- **`LiveServerSessionResumptionUpdate` Message:**
    - The server can send a `LiveServerSessionResumptionUpdate` message to the client. This message is defined in `google/genai/types.py`.
    - This message provides:
        - `new_handle`: An updated handle for the current session, which can be used for future resumption.
        - `resumable`: A boolean indicating if the session is currently in a state that can be resumed.
        - `last_consumed_client_message_index`: Helps in synchronizing message history if `transparent` resumption is used.
    - This mechanism allows the *logical session* to be maintained and continued even if the underlying WebSocket connection is new.
    - **Example JSON from server (illustrative):**
      A message received by the client via `await self._ws.recv()` and then parsed might look like this:
      ```json
      {
        "sessionResumptionUpdate": { // Field name as per LiveServerMessage type
          "newHandle": "new_session_handle_abc987",
          "resumable": true,
          "lastConsumedClientMessageIndex": 42 // If transparent resumption was active
        }
        // ... other possible fields in LiveServerMessage ...
      }
      ```
      The SDK user would access these fields through the `session_resumption_update` attribute of the parsed `types.LiveServerMessage` object.

### 4.1. Model-Specific Behaviors

-   The SDK source code itself does not generally detail specific timeout behaviors (e.g., idle timeouts, maximum session duration) or other session length limitations for different models.
-   These aspects are typically governed by the backend service for the specific model being used (e.g., `gemini-2.0-flash-live-001` vs. another live model).
-   Users should refer to the official documentation for the specific model or service for details on session lifecycle policies, quotas, and limits. The `LiveServerGoAway` message is the primary mechanism for the server to signal impending termination.

## 5. Explicit Client-Side Keep-Alives

- There is no evidence in `google/genai/live.py` or `google/genai/live_music.py` of the SDK sending explicit application-level keep-alive messages (e.g., custom pings or empty messages) solely for the purpose of keeping the session alive. The reliance is on the WebSocket protocol itself and the continuous receive loop.

## 6. Closing the Session

- **`AsyncSession.close()`:** The client can explicitly close the WebSocket connection using `await self._ws.close()`. This terminates the session from the client side.

In summary, session maintenance relies on the inherent persistence of WebSocket connections, continuous data reception acting as a liveness check, server-sent signals for graceful termination, and a system for session state resumption using handles.
