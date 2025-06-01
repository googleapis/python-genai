# Report 4: WebSocket Communication Analysis

This report details what is effectively sent and received via WebSockets, focusing on data formats (bytes, audio) and the handling of audio decoding.

## 1. General WebSocket Data Format

- **JSON Strings:** All communication between the SDK client and the live audio endpoint over WebSockets occurs via messages formatted as **JSON strings**.
- **UTF-8 Encoding:** These JSON strings are typically UTF-8 encoded when transmitted as WebSocket message payloads. The `websockets` library handles the underlying frame packing and unpacking.

## 2. Client-to-Server WebSocket Messages

The client sends various types of messages, all encapsulated as JSON strings:

1.  **Initial Setup Message (on connect):**
    -   **Content:** A JSON object, typically with a root key like `setup`. This object contains model selection, generation configurations, tool definitions, system instructions, and session resumption parameters.
    -   Example: `{"setup": {"model": "models/gemini-pro", "config": {"response_modalities": ["TEXT", "AUDIO"]}}}` (simplified).

2.  **`send_client_content` Payload:**
    -   **Content:** A JSON object with a root key `client_content`. The value contains:
        -   `turns`: An array of `Content` objects (each with `role` and `parts`).
        -   `turn_complete`: A boolean.
    -   Binary data within `Content` parts (e.g., `inlineData` for images/audio `Blob`s) is **base64 encoded** by the SDK before JSON serialization.
    -   Example: `{"client_content": {"turns": [{"role": "user", "parts": [{"text": "Hello"}, {"inlineData": {"mimeType": "audio/opus", "data": "BASE64_ENCODED_AUDIO"}}]}] , "turn_complete": true}}`

3.  **`send_realtime_input` Payload:**
    -   **Content:** A JSON object with a root key `realtime_input`. The value is a dictionary containing one of several specific keys based on the input type:
        -   `mediaChunks`: An array of `Blob` objects.
        -   `audio`: A single `Blob` object (for Google AI/mldev).
        -   `audioStreamEnd`: A boolean.
        -   `video`: A single `Blob` object (for Google AI/mldev).
        -   `text`: A string.
        -   `activityStart` / `activityEnd`: Objects indicating voice activity.
    -   Any raw `bytes` within `Blob.data` (e.g., audio samples, image data) are **base64 encoded** by the SDK (specifically by `_common.encode_unserializable_types`) to ensure they are valid JSON string values. The `mimeType` field in the `Blob` informs the server about the original format of the binary data.

4.  **`send_tool_response` Payload:**
    -   **Content:** A JSON object with a root key `tool_response`. The value contains:
        -   `functionResponses`: An array of `FunctionResponse` objects, each including the `id` of the tool call, the function `name`, and the `response` data (which itself must be JSON-serializable).

## 3. Server-to-Client WebSocket Messages

The server also sends JSON formatted messages, which the client receives and parses:

1.  **Message Parsing:**
    -   The client uses `await self._ws.recv()` to get raw message data.
    -   This data (typically bytes or a string, depending on the `websockets` library version and `decode` option) is parsed using `json.loads()`. This implies the server sends UTF-8 encoded JSON.

2.  **`LiveServerMessage` Content:**
    -   The parsed JSON is transformed into a `types.LiveServerMessage` Python object. This object can represent various server communications:
        -   `setup_complete`: Confirmation that the session setup was successful.
        -   `server_content`: (`LiveServerContent`) The primary way the model sends back content.
            -   Contains `model_turn` (a `types.Content` object).
            -   `Content.parts` can include `text` or `inline_data` (`types.Blob`).
            -   If `inline_data` is audio (e.g., `mimeType: "audio/opus"`), its `data` field will be a **base64 encoded string** representing the audio bytes. **`[voice is emitted here with dialogue]`** (after client-side decoding and playback).
            -   Also includes `input_transcription` and `output_transcription` (`types.Transcription`) which contain transcribed text and a `finished` boolean.
        -   `tool_call`: Requests the client to execute one or more functions.
        -   `tool_call_cancellation`: Instructs the client to cancel an ongoing tool call.
        -   `usage_metadata`: Provides token usage information.
        -   `go_away`: Signals the server's intent to close the session.
        -   `session_resumption_update`: Provides a new handle for session resumption.

## 4. Audio Data and Decoding

This section clarifies how audio bytes are handled and which component is responsible for decoding.

-   **Client Sending Audio:**
    1.  The SDK user provides audio data, often as raw bytes (e.g., PCM, or pre-encoded Opus bytes), along with a `mime_type` (e.g., `audio/pcm;rate=16000`, `audio/opus`) when calling `send_realtime_input` (e.g., via the `audio` or `media` parameter).
    2.  This raw byte data, if part of a `types.Blob` object, is **base64 encoded** by the SDK's `_common.encode_unserializable_types` function.
    3.  The resulting JSON message sent over WebSocket contains this base64 string for the audio data and the original `mime_type`.
    4.  **The server is responsible for:**
        -   Base64 decoding the received string back into bytes.
        -   Further decoding these bytes based on the provided `mime_type` (e.g., decoding Opus bytes into PCM for model processing).
    5.  The client SDK **does not** perform audio format decoding (like Opus to PCM) before sending; it only base64 encodes the provided bytes.

-   **Client Receiving Audio:**
    1.  The server sends audio as part of a `LiveServerMessage`, typically within `server_content.model_turn.parts`. An audio part will be a `Blob` with an appropriate `mime_type` (e.g., `audio/opus`, `audio/mp3`) and the `data` field containing **base64 encoded audio bytes**.
    2.  The SDK receives this JSON, parses it, and makes the `Blob` object (with its base64 data string and mime type) available to the user.
    3.  **The SDK itself does not automatically perform further decoding.**
    4.  **The SDK user is responsible for:**
        -   Taking the `blob.data` string.
        -   **Base64 decoding** it (e.g., using `base64.b64decode(blob.data)`) to get the raw audio bytes in the format specified by `blob.mime_type`.
        -   If the audio is in a compressed format (like Opus or MP3) and PCM data is needed (e.g., for playback), the user must use an appropriate audio library to **decode the audio format** from these raw bytes into PCM samples. **`[voice is emitted here with dialogue]`** (This is the point where, after all decoding, the audio would be played).


### 4.1. Example Packages for Audio Decoding

To handle the audio data received from the server, SDK users might need the following:

-   **`base64`**: (Python built-in module) For decoding the base64 encoded audio data string back into raw bytes.
-   **For Audio Format Decoding (from raw bytes to playable PCM, if not already PCM):**
    -   **Opus:**
        -   `opuslib`: A Python binding for the Opus library.
        -   `ffmpeg-python` or calling `ffmpeg` CLI: FFmpeg is a comprehensive multimedia framework that can handle Opus and many other formats.
        -   `soundfile` (which can use `libsndfile`): Might support Opus if `libsndfile` was compiled with Opus support.
    -   **MP3:**
        -   `pydub`: A high-level audio manipulation library that can use FFmpeg/libav or GStreamer for MP3 decoding.
        -   `ffmpeg-python` or `ffmpeg` CLI.
        -   `soundfile` (less common for direct MP3, but possible if `libsndfile` has MP3 support).
    -   **PCM/WAV:**
        -   `wave`: (Python built-in module) For reading/writing WAV files (which are often PCM).
        -   `soundfile`: Excellent for reading/writing various PCM-based formats like WAV, FLAC.
        -   `scipy.io.wavfile`: For reading/writing WAV files.

The choice of package depends on the specific audio format (`mime_type`) received from the server and the user's requirements.

### 4.2. Example: Base64 Decoding Received Audio

Here's a conceptual Python snippet showing how a client might handle a received audio part:

```python
import base64
# Assume 'server_message' is a parsed types.LiveServerMessage object
# and it contains an audio part.

# Conceptual function to play audio bytes (implementation specific)
def play_audio_bytes(audio_bytes, mime_type):
    print(f"Playing audio ({mime_type}, {len(audio_bytes)} bytes)... [conceptual playback]")
    # In a real app:
    # - If mime_type is 'audio/opus', decode Opus to PCM first.
    # - Then, use a library like simpleaudio, PyAudio, or platform APIs to play PCM.
    print("[actual voice is emitted here with dialogue]")


# ... inside the receive loop ...
# async for server_message in session.receive():
#     if server_message.server_content and server_message.server_content.model_turn:
#         for part in server_message.server_content.model_turn.parts:
#             if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
#                 print(f"Received audio part with mime_type: {part.inline_data.mime_type}")
#                 try:
#                     audio_data_base64 = part.inline_data.data
#                     if isinstance(audio_data_base64, str):
#                         # Assuming the data is a base64 encoded string
#                         decoded_audio_bytes = base64.b64decode(audio_data_base64)
#                         print(f"Base64 decoded {len(decoded_audio_bytes)} bytes of audio.")
#
#                         # Further decoding based on mime_type and playback would happen here
#                         # For example, if it's 'audio/opus', you'd use an Opus decoder.
#                         # If it's 'audio/pcm', it might be directly playable or need format info.
#                         play_audio_bytes(decoded_audio_bytes, part.inline_data.mime_type)
#
#                     elif isinstance(audio_data_base64, bytes):
#                         # If data is already bytes (less common for JSON, but good to check)
#                         # This might mean it's already decoded or it's raw binary from a non-JSON part if supported.
#                         # For live API, it's expected to be base64 string in JSON.
#                         print(f"Received raw audio bytes ({len(audio_data_base64)} bytes).")
#                         play_audio_bytes(audio_data_base64, part.inline_data.mime_type)
#
#                 except Exception as e:
#                     print(f"Error processing received audio data: {e}")
#             # ... handle text parts ...
```
This snippet focuses on the base64 decoding step. The actual audio playback or further format decoding (e.g., Opus to PCM) would require additional libraries and logic based on the `mime_type`.

**In summary:**

-   All WebSocket messages are JSON strings.
-   Binary payloads (like audio or image bytes within `Blob` objects) are transmitted as base64 encoded strings within the JSON structure.
-   The SDK handles the base64 encoding when sending and provides the base64 encoded string when receiving.
-   The actual audio format decoding (e.g., Opus to PCM, PCM to Opus) is handled by the **server when it receives audio** from the client, and by the **SDK user when they receive audio** from the server. The SDK only passes through the mime type and the (base64 encoded) bytes.
-   **`[voice is emitted here with dialogue]`** markers in this and other reports indicate the conceptual point at which the user would hear spoken output from the model, after the client application has received, base64-decoded, and then audio-decoded (if necessary) the audio data sent by the server.
