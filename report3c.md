# Report 3c: Analysis of `send_tool_response`

This report details what is effectively sent by the SDK when the `AsyncSession.send_tool_response` method is called. This method is used to return the results of function calls (tool executions) requested by the model.

## 1. Method Overview

- **Signature:**
  ```python
  async def send_tool_response(
      self,
      *,
      function_responses: Union[
          types.FunctionResponseOrDict,
          Sequence[types.FunctionResponseOrDict],
      ],
  ) -> None:
  ```
- **Purpose:** When the model, during a live session, issues a tool call (received by the client as a `LiveServerToolCall` message containing `function_calls`), the client is expected to execute the specified function(s). After execution, this `send_tool_response` method is used to send the outcome(s) back to the model.
- **Tool Definition:** The set of available tools (functions) that the model can call is initially declared in the `config.tools` argument passed to `client.aio.live.connect` during session setup.

## 2. Data Processing Steps

The `function_responses` provided to the method undergo the following processing:

1.  **Input Normalization (`t.t_tool_response`):**
    -   The `function_responses` argument (which can be a single `types.FunctionResponse` object, its dictionary equivalent, or a sequence of these) is processed by the `google.genai._transformers.t_tool_response` function.
    -   This step normalizes the input into a `types.LiveClientToolResponse` object. The primary field of this object is `function_responses`, which is a list of `types.FunctionResponse` objects.
    -   Each `types.FunctionResponse` object encapsulates:
        -   `id`: A unique identifier for the function call, which **must** match the `id` from the corresponding `FunctionCall` object received from the server (especially critical for Google AI/mldev).
        -   `name`: The name of the function that was executed.
        -   `response`: The actual result (data) from the function's execution. This is typically a dictionary representing a JSON object.

2.  **Platform-Specific Conversion (`_live_converters`):**
    -   The `types.LiveClientToolResponse` object is then converted into a dictionary format appropriate for the target backend (Vertex AI or Google AI) using functions from `google/genai/_live_converters.py`:
        -   **For Vertex AI (`_LiveClientToolResponse_to_vertex`):**
            -   The list of `FunctionResponse` objects from `LiveClientToolResponse.function_responses` is processed. Each `FunctionResponse` is converted by `_FunctionResponse_to_vertex`.
            -   `_FunctionResponse_to_vertex` maps:
                -   `id` to `id`.
                -   `name` to `name`.
                -   `response` to `response`.
        -   **For Google AI (mldev) (`_LiveClientToolResponse_to_mldev`):**
            -   Similar to Vertex, it processes the list of `FunctionResponse` objects using `_FunctionResponse_to_mldev`.
            -   `_FunctionResponse_to_mldev` maps:
                -   `id` to `id`. (A `ValueError` is raised by `send_tool_response` if an `id` is missing for any function response when targeting mldev).
                -   `name` to `name`.
                -   `response` to `response`.
                -   It also supports `will_continue` and `scheduling` fields, not used by Vertex.

3.  **Wrapping the Payload:**
    -   The dictionary resulting from the platform-specific conversion (`tool_response_dict`) is then wrapped within another dictionary, under the key `"tool_response"`:
        ```json
        {
          "tool_response": tool_response_dict
        }
        ```

4.  **JSON Serialization:**
    -   This final wrapped dictionary is serialized into a JSON string using `json.dumps()`.

5.  **WebSocket Transmission:**
    -   The serialized JSON string is sent over the active WebSocket connection:
        `await self._ws.send(json_string)`

## 3. Effective Data Sent (Illustrative Structure)

The data effectively sent over the WebSocket is a JSON string. Here's an illustrative structure:

```json
{
  "tool_response": {
    "functionResponses": [ // For Google AI (mldev), field name is 'functionResponses'
                           // For Vertex AI, field name is also 'functionResponses'
      {
        "id": "id_from_server_tool_call_123", // Matches the ID from the server's request
        "name": "turn_on_the_lights",
        "response": { // The actual data returned by the executed tool
          "status": "success",
          "detail": "Living room lights turned on."
        }
      }
      // ... more function responses if multiple tools were called or batched
    ]
  }
}
```

## 4. Extended Code Example: 10-Turn Dialogue with Tool Calls

This section provides a verbose, conceptual 10-turn dialogue simulation. It demonstrates how `send_client_content` can lead to tool calls, how the client might (mock) execute those tools, and how `send_tool_response` is used to return results, followed by further model interaction. This example emphasizes the flow and potential for spoken dialogue.

### 4.1. Required Packages

```python
import google.generativeai as genai
from google.generativeai import types
import asyncio
import os
import json # For tool response data
import time # For simulating delays
from typing import Optional # For type hinting

# For loading API keys from .env in examples (optional)
# from dotenv import load_dotenv
# load_dotenv()

# --- Mock Tool Implementation ---
# In a real application, these functions would perform actual operations.

# Mock database of smart home devices
mock_smart_home_devices = {
    "living room lamp": {"type": "light", "status": "off", "brightness": 0, "color": "white"},
    "kitchen thermostat": {"type": "thermostat", "status": "idle", "temperature_celsius": 20},
    "front door lock": {"type": "lock", "status": "locked"}
}

def get_device_status(device_name: str) -> dict:
    """Gets the current status of a smart home device."""
    print(f"[TOOL EXECUTING] get_device_status for: {device_name}")
    if device_name.lower() in mock_smart_home_devices:
        return {"device_name": device_name, "status": mock_smart_home_devices[device_name.lower()]["status"]}
    return {"error": "Device not found"}

def set_device_status(device_name: str, new_status: str, setting: Optional[dict] = None) -> dict:
    """Sets the status or a specific setting of a smart home device."""
    print(f"[TOOL EXECUTING] set_device_status for: {device_name} to {new_status} with settings: {setting}")
    device_name_lower = device_name.lower()
    if device_name_lower in mock_smart_home_devices:
        current_device = mock_smart_home_devices[device_name_lower]
        if new_status in ["on", "off", "locked", "unlocked", "idle", "heating", "cooling"]:
            current_device["status"] = new_status

        if setting:
            if "temperature_celsius" in setting and current_device["type"] == "thermostat":
                current_device["temperature_celsius"] = setting["temperature_celsius"]
            if "brightness" in setting and current_device["type"] == "light":
                current_device["brightness"] = setting["brightness"]
            if "color" in setting and current_device["type"] == "light":
                current_device["color"] = setting["color"]

        return {"device_name": device_name, "status": current_device["status"], "settings_updated": setting or {}}
    return {"error": "Device not found or invalid status/setting"}

# Mapping function names to actual functions
available_tools = {
    "get_device_status": get_device_status,
    "set_device_status": set_device_status,
}
# --- End Mock Tool Implementation ---
```

### 4.2. Example Scenario: Smart Home Control

This simulation uses a model like `gemini-2.0-flash-live-001` (Google AI) or `gemini-2.0-flash-live-preview-04-09` (Vertex AI).

```python
async def run_tool_call_dialogue_example():
    # --- Client and Model Setup ---
    if os.environ.get('GOOGLE_GENAI_USE_VERTEXAI'):
        client = genai.Client(vertexai=True, project=os.environ.get("VERTEX_PROJECT_ID"), location=os.environ.get("VERTEX_LOCATION"))
        MODEL_NAME = 'gemini-2.0-flash-live-preview-04-09'
    else:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        client = genai.Client()
        MODEL_NAME = 'gemini-2.0-flash-live-001'
    print(f"Connecting to model: {MODEL_NAME}")

    # --- Tool Definition for the Model ---
    # Define tools for the model using FunctionDeclaration
    tool_declarations = [
        types.FunctionDeclaration(
            name="get_device_status",
            description="Gets the current status of a specified smart home device.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "device_name": types.Schema(type=types.Type.STRING, description="The name of the device, e.g., 'living room lamp'.")
                },
                required=["device_name"]
            )
        ),
        types.FunctionDeclaration(
            name="set_device_status",
            description="Sets the status or a specific setting of a smart home device. For lights, 'on' or 'off'. For locks, 'locked' or 'unlocked'. For thermostats, temperature can be set.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "device_name": types.Schema(type=types.Type.STRING, description="The name of the device."),
                    "new_status": types.Schema(type=types.Type.STRING, description="The desired new status (e.g., 'on', 'off', 'locked')."),
                    "setting": types.Schema(
                        type=types.Type.OBJECT,
                        description="Optional settings like temperature for thermostats or brightness/color for lights.",
                        properties={
                            "temperature_celsius": types.Schema(type=types.Type.INTEGER, description="Temperature in Celsius for thermostats."),
                            "brightness": types.Schema(type=types.Type.INTEGER, description="Brightness level (0-100) for lights."),
                            "color": types.Schema(type=types.Type.STRING, description="Color name for lights (e.g., 'blue').")
                        }
                    )
                },
                required=["device_name", "new_status"]
            )
        )
    ]

    connect_config = types.LiveConnectConfig(
        response_modalities=[types.Modality.TEXT, types.Modality.AUDIO], # Requesting audio for spoken dialogue
        tools=[types.Tool(function_declarations=tool_declarations)]
    )

    # --- Dialogue Simulation ---
    dialogue_turns = [
        # Turn 1 (User)
        {"role": "user", "text": "Is the living room lamp on?"},
        # Turn 2 (Model -> Tool Call) - Expected: get_device_status for "living room lamp"
        # Turn 3 (Client -> Tool Response) - Status of lamp
        # Turn 4 (Model) - "No, the living room lamp is currently off." [voice is emitted here with dialogue]
        # Turn 5 (User)
        {"role": "user", "text": "Okay, please turn it on and set its color to blue."},
        # Turn 6 (Model -> Tool Call) - Expected: set_device_status for "living room lamp" to "on", color "blue"
        # Turn 7 (Client -> Tool Response) - Confirmation of lamp status change
        # Turn 8 (Model) - "Alright, I've turned on the living room lamp and set its color to blue." [voice is emitted here with dialogue]
        # Turn 9 (User)
        {"role": "user", "text": "What's the kitchen thermostat set to?"},
        # Turn 10 (Model -> Tool Call) - Expected: get_device_status for "kitchen thermostat"
        # ... and so on. We'll simulate these steps.
    ]

    current_turn_index = 0
    server_message = None # To satisfy the check after the loop

    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=connect_config) as session:
            print("Session connected with smart home tools.")

            while current_turn_index < len(dialogue_turns):
                turn_data = dialogue_turns[current_turn_index]
                print(f"\n--- Turn {current_turn_index + 1} ({turn_data['role']}) ---")

                if turn_data["role"] == "user":
                    print(f"User says: {turn_data['text']}")
                    await session.send_client_content(
                        turns=types.Content(role="user", parts=[types.Part(text=turn_data["text"])]),
                        turn_complete=True
                    )
                    current_turn_index += 1 # Move to expect model response or tool call

                # Expecting model response / tool call
                print("Waiting for model action...")
                async for server_message in session.receive():
                    if server_message.server_content:
                        if server_message.server_content.model_turn:
                            for part in server_message.server_content.model_turn.parts:
                                if part.text:
                                    print(f"Model says: {part.text}")
                                    # [voice is emitted here with dialogue]
                                    if types.Modality.AUDIO in connect_config.response_modalities:
                                         print("[voice is emitted here with dialogue]")

                        if server_message.server_content.turn_complete:
                            print("Model completed its turn.")
                            # If this was a direct answer, and not leading to another user turn in our script,
                            # we might break or expect the next user turn from dialogue_turns.
                            if current_turn_index >= len(dialogue_turns) or dialogue_turns[current_turn_index]["role"] != "user":
                                # If model completes turn and next is not user, implies we need to break or handle differently
                                pass # Allow loop to continue if more scripted turns exist
                            break # Break from receive loop to allow next user turn or end

                    elif server_message.tool_call:
                        print("Model requests tool call(s):")
                        function_responses_to_send = []
                        for fc in server_message.tool_call.function_calls:
                            print(f"  Function Call ID: {fc.id}")
                            print(f"  Function Name: {fc.name}")
                            print(f"  Arguments: {fc.args}")

                            if fc.name in available_tools:
                                tool_function = available_tools[fc.name]
                                try:
                                    # Simulate tool execution
                                    result = tool_function(**fc.args)
                                    function_responses_to_send.append(
                                        types.FunctionResponse(id=fc.id, name=fc.name, response=result)
                                    )
                                except Exception as e:
                                    print(f"[TOOL ERROR] Error executing {fc.name}: {e}")
                                    function_responses_to_send.append(
                                        types.FunctionResponse(id=fc.id, name=fc.name, response={"error": str(e)})
                                    )
                            else:
                                print(f"[TOOL ERROR] Unknown function: {fc.name}")
                                function_responses_to_send.append(
                                    types.FunctionResponse(id=fc.id, name=fc.name, response={"error": "Function not found"})
                                )

                        if function_responses_to_send:
                            print("Sending tool responses to model...")
                            await session.send_tool_response(function_responses=function_responses_to_send)
                            # current_turn_index might not advance here, as we expect model to respond to tool results
                        # After sending tool response, stay in receive loop for model's next message
                        # Do not break here, let the receive loop continue

                    elif server_message.error:
                        print(f"Received an error: {server_message.error}")
                        return # End session on error

                    # If a tool call was processed, we expect another server_message, so don't break receive loop.
                    # If it was server_content and turn_complete, the outer loop will advance or break.
                    if server_message.server_content and server_message.server_content.turn_complete:
                         break # Break from receive to allow next turn in dialogue_turns

                if current_turn_index >= len(dialogue_turns) and not (server_message and server_message.tool_call): # If no more user turns and last wasn't a tool call that needs a model reply
                    print("End of scripted dialogue.")
                    break


            print("\nDialogue simulation finished.")
            await session.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

# To run the example:
# asyncio.run(run_tool_call_dialogue_example())
```

### 4.3. Interaction Flow Explanation

1.  **Setup**:
    *   The client initializes, specifying `MODEL_NAME`.
    *   `tool_declarations` are created using `types.FunctionDeclaration` to describe `get_device_status` and `set_device_status` to the model, including their parameters.
    *   `LiveConnectConfig` includes these tools and requests `TEXT` and `AUDIO` response modalities.

2.  **Turn 1 (User -> Model)**:
    *   User: "Is the living room lamp on?"
    *   Sent via `send_client_content`.

3.  **Turn 2 (Model -> Tool Call)**:
    *   The model processes the query and determines it needs to call `get_device_status`.
    *   Server sends a `LiveServerMessage` with `tool_call` populated. This includes a `FunctionCall` object with:
        *   `id`: A unique ID for this call (e.g., "call\_abc123").
        *   `name`: "get\_device\_status".
        *   `args`: `{"device_name": "living room lamp"}`.

4.  **Turn 3 (Client: Tool Execution & `send_tool_response`)**:
    *   The client's `receive` loop gets the `tool_call`.
    *   It finds the `get_device_status` function in its `available_tools`.
    *   **`[TOOL EXECUTING]`**: The `get_device_status("living room lamp")` function is called (mock execution). It returns `{"device_name": "living room lamp", "status": "off"}`.
    *   The client constructs a `types.FunctionResponse` with the original `id` ("call\_abc123"), `name`, and the `response` dictionary.
    *   `await session.send_tool_response(function_responses=[...])` sends this back.
    *   The JSON sent would be structured like:
        ```json
        {
          "tool_response": {
            "functionResponses": [{
              "id": "call_abc123",
              "name": "get_device_status",
              "response": {"device_name": "living room lamp", "status": "off"}
            }]
          }
        }
        ```

5.  **Turn 4 (Model -> User)**:
    *   The model receives the tool's result.
    *   It formulates a natural language response: "No, the living room lamp is currently off."
    *   Server sends `LiveServerMessage` with `server_content` (text and/or audio).
    *   **`[voice is emitted here with dialogue]`**: Client plays the audio part.

6.  **Turn 5 (User -> Model)**:
    *   User: "Okay, please turn it on and set its color to blue."
    *   Sent via `send_client_content`.

7.  **Turn 6 (Model -> Tool Call)**:
    *   Model determines it needs `set_device_status`.
    *   Server sends `tool_call` for `set_device_status` with `args`: `{"device_name": "living room lamp", "new_status": "on", "setting": {"color": "blue"}}`. (ID: "call\_def456")

8.  **Turn 7 (Client: Tool Execution & `send_tool_response`)**:
    *   **`[TOOL EXECUTING]`**: `set_device_status` is called. Mock device status is updated. Returns `{"device_name": "living room lamp", "status": "on", "settings_updated": {"color": "blue"}}`.
    *   Client sends `FunctionResponse` via `send_tool_response` (ID: "call\_def456").

9.  **Turn 8 (Model -> User)**:
    *   Model: "Alright, I've turned on the living room lamp and set its color to blue."
    *   **`[voice is emitted here with dialogue]`**.

10. **Turn 9 (User -> Model)**:
    *   User: "What's the kitchen thermostat set to?"
    *   Sent via `send_client_content`.

11. **Turn 10 (Model -> Tool Call)**:
    *   Model requests `get_device_status` for "kitchen thermostat". (ID: "call\_ghi789")
    *   *(The dialogue would continue with the client executing this and the model responding...)*

This extended example shows the back-and-forth nature of conversations involving tool use, with `send_tool_response` being critical for providing the model with the information it needs from the external tools. The `[voice is emitted here with dialogue]` markers indicate points where the model's speech synthesis (if configured and generated) would be played out.

This method allows the client to provide the necessary feedback to the model after tool execution, enabling the model to continue its reasoning process with the results of the tool's operation.
