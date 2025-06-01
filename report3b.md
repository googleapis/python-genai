# Report 3b: Analysis of `send_realtime_input`

This report details what is effectively sent by the SDK when the `AsyncSession.send_realtime_input` method is called.

## 1. Method Overview

- **Signature:**
  ```python
  async def send_realtime_input(
      self,
      *,
      media: Optional[types.BlobImageUnionDict] = None,
      audio: Optional[types.BlobOrDict] = None,
      audio_stream_end: Optional[bool] = None,
      video: Optional[types.BlobImageUnionDict] = None,
      text: Optional[str] = None,
      activity_start: Optional[types.ActivityStartOrDict] = None,
      activity_end: Optional[types.ActivityEndOrDict] = None,
  ) -> None:
  ```
- **Purpose:** This method is designed for sending real-time data streams to the model, such as audio chunks, video frames (as images), or discrete text messages. It is optimized for low latency and responsiveness. The API may use Voice Activity Detection (VAD) for audio inputs. Unlike `send_client_content`, order of processing for these inputs relative to other inputs might not be strictly guaranteed.
- **Constraint:** Only one of the keyword arguments (`media`, `audio`, `audio_stream_end`, `video`, `text`, `activity_start`, `activity_end`) can be provided per call.

## 2. Data Processing Steps

The input to `send_realtime_input` is processed as follows before WebSocket transmission:

1.  **Argument Validation and Collection:**
    -   The method first gathers all provided keyword arguments.
    -   It enforces that exactly one argument is non-None. If this condition isn't met, a `ValueError` is raised.

2.  **Input Standardization (`types.LiveSendRealtimeInputParameters`):**
    -   The single, validated keyword argument and its value are used to create an instance of `types.LiveSendRealtimeInputParameters` using `model_validate`. This Pydantic model ensures the input conforms to one of its defined fields.

3.  **Platform-Specific Conversion (`_live_converters`):**
    -   The `LiveSendRealtimeInputParameters` object is then converted into a dictionary suitable for the target backend (Vertex AI or Google AI) using functions from `google/genai/_live_converters.py`:
        -   **For Vertex AI (`_LiveSendRealtimeInputParameters_to_vertex`):**
            -   `media`: Mapped to `mediaChunks`. Each item is processed by `google.genai._transformers.t_blobs`.
            -   `audio_stream_end`: Mapped to `audioStreamEnd`.
            -   `activity_start`: Mapped to `activityStart` (processed by `_ActivityStart_to_vertex`).
            -   `activity_end`: Mapped to `activityEnd` (processed by `_ActivityEnd_to_vertex`).
            -   **Note:** The `audio`, `video`, and `text` parameters will raise a `ValueError` if used with Vertex AI through this converter, indicating they should likely be sent via the `media` field or are not directly supported in this way for Vertex realtime streams.
        -   **For Google AI (mldev) (`_LiveSendRealtimeInputParameters_to_mldev`):**
            -   `media`: Mapped to `mediaChunks` (processed by `google.genai._transformers.t_blobs`).
            -   `audio`: Mapped to `audio` (processed by `google.genai._transformers.t_audio_blob`). This typically involves creating a `types.Blob` with the audio data and mime type.
            -   `audio_stream_end`: Mapped to `audioStreamEnd` (boolean).
            -   `video`: Mapped to `video` (processed by `google.genai._transformers.t_image_blob`).
            -   `text`: Mapped to `text` (string).
            -   `activity_start`: Mapped to `activityStart` (processed by `_ActivityStart_to_mldev`).
            -   `activity_end`: Mapped to `activityEnd` (processed by `_ActivityEnd_to_mldev`).

4.  **Encoding Unserializable Types (`_common.encode_unserializable_types`):**
    -   The resulting dictionary (`realtime_input_dict`) is processed by `google.genai._common.encode_unserializable_types`.
    -   This function is crucial for data like `bytes` found in `types.Blob` objects (e.g., raw audio data, image data). It **base64 encodes** these `bytes` to ensure they are valid JSON values. Other non-standard types might also be converted here.

5.  **Wrapping the Payload:**
    -   The processed and encoded dictionary is wrapped within another dictionary, under the key `"realtime_input"`:
        ```json
        {
          "realtime_input": realtime_input_dict
        }
        ```

6.  **JSON Serialization:**
    -   This final wrapped dictionary is serialized into a JSON string using `json.dumps()`.

7.  **WebSocket Transmission:**
    -   The serialized JSON string is sent over the active WebSocket connection:
        `await self._ws.send(json_string)`

## 3. Effective Data Sent (Illustrative Structures)

The data sent over the WebSocket is a JSON string. The exact structure of `realtime_input_dict` depends on the argument used.

**Example 1: Sending audio (Google AI/mldev)**

If `send_realtime_input(audio=types.Blob(data=b'...', mime_type='audio/pcm;rate=16000'))` is called:

```json
{
  "realtime_input": {
    "audio": {
      "mimeType": "audio/pcm;rate=16000",
      "data": "BASE64_ENCODED_AUDIO_BYTES" // Result of base64 encoding
    }
  }
}
```

**Example 2: Sending media (generic, could be image or audio for Vertex/Google AI)**

If `send_realtime_input(media=PIL.Image.open('image.jpg'))` is called (assuming an image that gets converted to a `types.Blob`):

```json
{
  "realtime_input": {
    "mediaChunks": [ // t_blobs can produce a list
      {
        "mimeType": "image/jpeg", // Or appropriate mime type
        "data": "BASE64_ENCODED_IMAGE_BYTES" // Result of base64 encoding
      }
    ]
  }
}
```

**Example 3: Sending text (Google AI/mldev)**

If `send_realtime_input(text="Hello")` is called:

```json
{
  "realtime_input": {
    "text": "Hello"
  }
}
```

**Example 4: Sending audio stream end**

If `send_realtime_input(audio_stream_end=True)` is called:

```json
{
  "realtime_input": {
    "audioStreamEnd": true
  }
}
```

## 4. Code Examples and Interaction Flow

This section provides conceptual examples of using `send_realtime_input` for text and audio, and illustrates the interaction flow, including where voice output might occur.

### 4.1. Required Packages

```python
import google.generativeai as genai
from google.generativeai import types
import asyncio
import os
import time # For simulating audio streaming
import base64 # For handling audio data
from pathlib import Path # For reading audio files

# For loading API keys from .env in examples
# from dotenv import load_dotenv
# load_dotenv()

# For audio processing in a real application, you might need:
# import soundfile  # For reading/writing audio files
# import numpy as np # For audio data manipulation
```

### 4.2. Example Scenario: Sending Text and Streaming Audio

This example demonstrates sending a text message and then streaming chunks of an audio file. It assumes a model like `gemini-2.0-flash-live-001` (Google AI) or `gemini-2.0-flash-live-preview-04-09` (Vertex AI).

```python
async def run_realtime_input_example():
    # Configure the client (ensure API key is set, or ADC for Vertex)
    if os.environ.get('GOOGLE_GENAI_USE_VERTEXAI'):
        client = genai.Client(vertexai=True, project=os.environ.get("VERTEX_PROJECT_ID"), location=os.environ.get("VERTEX_LOCATION"))
        MODEL_NAME = 'gemini-2.0-flash-live-preview-04-09' # Or other suitable live model
        # Note: For Vertex, audio is typically sent via the 'media' parameter.
        # This example primarily shows the 'audio' parameter flow relevant to Google AI (mldev).
        # To adapt for Vertex, audio_bytes would be wrapped in types.Blob and sent via 'media'.
    else:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        client = genai.Client()
        MODEL_NAME = 'gemini-2.0-flash-live-001'

    print(f"Connecting to model: {MODEL_NAME}")

    connect_config = types.LiveConnectConfig(
        response_modalities=[types.Modality.TEXT, types.Modality.AUDIO],
        realtime_input_config=types.RealtimeInputConfig( # Example VAD tuning
            automatic_activity_detection=types.AutomaticActivityDetection(
                silence_duration_ms=2000, # Longer silence before considering speech ended
                prefix_padding_ms=200
            )
        )
    )

    # Create a dummy audio file for the example (e.g., PCM 16-bit, 16kHz, mono)
    # In a real scenario, this would be your actual audio source.
    SAMPLE_RATE = 16000
    dummy_audio_path = Path("dummy_audio.pcm")
    if not dummy_audio_path.exists():
        # Create a few seconds of silence or simple tone for testing
        # For simplicity, creating a small, potentially invalid PCM for structure.
        # A real PCM file would have proper WAV headers or be raw samples.
        # This is just to have some bytes to send.
        silence_duration_seconds = 2
        num_samples = SAMPLE_RATE * silence_duration_seconds
        # 16-bit PCM means 2 bytes per sample
        dummy_audio_data = b'\x00\x00' * num_samples
        dummy_audio_path.write_bytes(dummy_audio_data)
        print(f"Created dummy audio file: {dummy_audio_path}")


    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=connect_config) as session:
            print("Session connected.")

            # 1. Send an initial text message (Google AI / mldev specific parameter)
            if not client._api_client.vertexai: # text param is mldev-specific for send_realtime_input
                initial_text = "I'm about to send you some audio. Please transcribe it."
                print(f"Sending realtime text: '{initial_text}'")
                await session.send_realtime_input(text=initial_text)
                # Server might send an acknowledgement or interim text based on this.
                # [voice is emitted here with dialogue] if model responds with audio to this text.
                await asyncio.sleep(0.5) # Give a moment for potential quick reply
            else:
                # For Vertex, send text via send_client_content or as a media part if needed
                print("Skipping realtime text for Vertex (use send_client_content or media).")


            # 2. Stream audio data
            print(f"Streaming audio from {dummy_audio_path}...")
            chunk_size = 3200  # Bytes per chunk (e.g., 100ms of 16kHz 16-bit mono audio)

            with open(dummy_audio_path, "rb") as f:
                while True:
                    audio_chunk = f.read(chunk_size)
                    if not audio_chunk:
                        break

                    print(f"Sending audio chunk of size {len(audio_chunk)} bytes.")
                    if client._api_client.vertexai:
                        # For Vertex AI, audio should be sent via 'media'
                        await session.send_realtime_input(
                            media=types.Blob(data=audio_chunk, mime_type=f"audio/pcm;rate={SAMPLE_RATE}")
                        )
                    else:
                        # For Google AI (mldev), 'audio' parameter can be used
                        await session.send_realtime_input(
                            audio=types.Blob(data=audio_chunk, mime_type=f"audio/pcm;rate={SAMPLE_RATE}")
                        )
                    # Simulate real-time streaming interval
                    await asyncio.sleep(0.1) # 100ms delay

            # 3. Signal end of audio stream
            print("Sending audio stream end signal.")
            await session.send_realtime_input(audio_stream_end=True)

            # 4. Receive responses
            print("Waiting for final responses...")
            # [voice is emitted here with dialogue] as model processes audio and responds.
            async for server_message in session.receive():
                if server_message.server_content:
                    if server_message.server_content.input_transcription:
                        transcription = server_message.server_content.input_transcription
                        print(f"Input Transcription: '{transcription.text}' (Finished: {transcription.finished})")

                    if server_message.server_content.model_turn:
                        for part in server_message.server_content.model_turn.parts:
                            if part.text:
                                print(f"Received model text: {part.text}")
                            if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                                print(f"Received model audio (mime_type: {part.inline_data.mime_type}). Playing... [conceptual]")
                                print("[voice is emitted here with dialogue]")

                    if server_message.server_content.turn_complete:
                        print("Model has completed its turn.")
                        break
                elif server_message.error:
                    print(f"Received an error: {server_message.error}")
                    break

            print("Closing session.")
            await session.close()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if dummy_audio_path.exists():
            dummy_audio_path.unlink() # Clean up dummy file

# To run the example:
# asyncio.run(run_realtime_input_example())
```

### 4.3. Interaction Flow Explanation

1.  **Connection & Setup:** Similar to `send_client_content`, the client connects, specifying `response_modalities` (including `AUDIO` if spoken replies are desired) and potentially `realtime_input_config` for VAD tuning.
2.  **Sending Realtime Text (Google AI/mldev):**
    -   `session.send_realtime_input(text=...)` sends a discrete text message.
    -   The model might provide an immediate textual or spoken acknowledgement or response. `[voice is emitted here with dialogue]` could occur if the model replies with audio.
3.  **Streaming Audio:**
    -   The example reads an audio file in chunks.
    -   Each chunk is sent using `session.send_realtime_input(audio=types.Blob(...))` for Google AI, or `session.send_realtime_input(media=types.Blob(...))` for Vertex AI. The `mime_type` (e.g., `audio/pcm;rate=16000`) is crucial.
    -   A small delay (`asyncio.sleep`) simulates real-time capture.
4.  **Ending Audio Stream:**
    -   `session.send_realtime_input(audio_stream_end=True)` signals that no more audio chunks for the current utterance will be sent. This helps the VAD and the model determine the end of user speech.
5.  **Receiving Responses:**
    -   The `session.receive()` loop processes incoming messages.
    -   **Input Transcription:** The server may send `LiveServerMessage` objects containing `input_transcription` (with `text` and `finished` fields) as it processes the audio.
    -   **Model Response:** After processing the audio (and potentially the initial text), the model will send its response.
        -   **`[voice is emitted here with dialogue]`**: If the response includes audio parts (`inline_data` with an audio MIME type), this is where the voice output would be conceptually played by the client after base64 decoding the data.
        -   Text parts are also processed.
    -   The loop continues until the model signals `turn_complete`.

This method is suited for scenarios requiring immediate processing of inputs like live voice commands or continuous sensor data.

### 4.4. Key characteristics of the sent data

-   It's always a JSON object with a top-level key `realtime_input`.
-   The value of `realtime_input` is a dictionary containing one specific key corresponding to the input type (e.g., `audio`, `mediaChunks`, `text`, `audioStreamEnd`).
-   Binary data (like audio content in `Blob.data` or image data) is **base64 encoded** to be part of the JSON string.
-   MIME types are included for `Blob` data to inform the server about the data format.
