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

"""[Preview] Live API client."""


import logging
from typing import Any, Dict, Optional, Union

from . import _api_module
from . import _common
from . import _transformers as t
from . import types
from ._api_client import BaseApiClient
from ._common import get_value_by_path as getv
from ._common import set_value_by_path as setv
from .models import _Content_from_mldev
from .models import _Content_from_vertex
from .models import _Content_to_mldev
from .models import _Content_to_vertex
from .models import _GenerateContentConfig_to_mldev
from .models import _GenerateContentConfig_to_vertex
from .models import _SafetySetting_to_mldev
from .models import _SafetySetting_to_vertex
from .models import _SpeechConfig_to_mldev
from .models import _SpeechConfig_to_vertex
from .models import _Tool_to_mldev
from .models import _Tool_to_vertex

logger = logging.getLogger('google_genai._live_converters')

_FUNCTION_RESPONSE_REQUIRES_ID = (
    'FunctionResponse request must have an `id` field from the'
    ' response of a ToolCall.FunctionalCalls in Google AI.'
)

def _SessionResumptionConfig_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['handle']) is not None:
    setv(to_object, ['handle'], getv(from_object, ['handle']))

  if getv(from_object, ['transparent']) is not None:
    raise ValueError('transparent parameter is not supported in Gemini API.')

  return to_object


def _SessionResumptionConfig_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['handle']) is not None:
    setv(to_object, ['handle'], getv(from_object, ['handle']))

  if getv(from_object, ['transparent']) is not None:
    setv(to_object, ['transparent'], getv(from_object, ['transparent']))

  return to_object


def _AudioTranscriptionConfig_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}

  return to_object


def _AudioTranscriptionConfig_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}

  return to_object


def _AutomaticActivityDetection_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['disabled']) is not None:
    setv(to_object, ['disabled'], getv(from_object, ['disabled']))

  if getv(from_object, ['start_of_speech_sensitivity']) is not None:
    setv(
        to_object,
        ['startOfSpeechSensitivity'],
        getv(from_object, ['start_of_speech_sensitivity']),
    )

  if getv(from_object, ['end_of_speech_sensitivity']) is not None:
    setv(
        to_object,
        ['endOfSpeechSensitivity'],
        getv(from_object, ['end_of_speech_sensitivity']),
    )

  if getv(from_object, ['prefix_padding_ms']) is not None:
    setv(
        to_object, ['prefixPaddingMs'], getv(from_object, ['prefix_padding_ms'])
    )

  if getv(from_object, ['silence_duration_ms']) is not None:
    setv(
        to_object,
        ['silenceDurationMs'],
        getv(from_object, ['silence_duration_ms']),
    )

  return to_object


def _AutomaticActivityDetection_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['disabled']) is not None:
    setv(to_object, ['disabled'], getv(from_object, ['disabled']))

  if getv(from_object, ['start_of_speech_sensitivity']) is not None:
    setv(
        to_object,
        ['startOfSpeechSensitivity'],
        getv(from_object, ['start_of_speech_sensitivity']),
    )

  if getv(from_object, ['end_of_speech_sensitivity']) is not None:
    setv(
        to_object,
        ['endOfSpeechSensitivity'],
        getv(from_object, ['end_of_speech_sensitivity']),
    )

  if getv(from_object, ['prefix_padding_ms']) is not None:
    setv(
        to_object, ['prefixPaddingMs'], getv(from_object, ['prefix_padding_ms'])
    )

  if getv(from_object, ['silence_duration_ms']) is not None:
    setv(
        to_object,
        ['silenceDurationMs'],
        getv(from_object, ['silence_duration_ms']),
    )

  return to_object


def _RealtimeInputConfig_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['automatic_activity_detection']) is not None:
    setv(
        to_object,
        ['automaticActivityDetection'],
        _AutomaticActivityDetection_to_mldev(
            api_client,
            getv(from_object, ['automatic_activity_detection']),
            to_object,
        ),
    )

  if getv(from_object, ['activity_handling']) is not None:
    setv(
        to_object,
        ['activityHandling'],
        getv(from_object, ['activity_handling']),
    )

  if getv(from_object, ['turn_coverage']) is not None:
    setv(to_object, ['turnCoverage'], getv(from_object, ['turn_coverage']))

  return to_object


def _RealtimeInputConfig_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['automatic_activity_detection']) is not None:
    setv(
        to_object,
        ['automaticActivityDetection'],
        _AutomaticActivityDetection_to_vertex(
            api_client,
            getv(from_object, ['automatic_activity_detection']),
            to_object,
        ),
    )

  if getv(from_object, ['activity_handling']) is not None:
    setv(
        to_object,
        ['activityHandling'],
        getv(from_object, ['activity_handling']),
    )

  if getv(from_object, ['turn_coverage']) is not None:
    setv(to_object, ['turnCoverage'], getv(from_object, ['turn_coverage']))

  return to_object


def _SlidingWindow_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['target_tokens']) is not None:
    setv(to_object, ['targetTokens'], getv(from_object, ['target_tokens']))

  return to_object


def _SlidingWindow_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['target_tokens']) is not None:
    setv(to_object, ['targetTokens'], getv(from_object, ['target_tokens']))

  return to_object


def _ContextWindowCompressionConfig_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['trigger_tokens']) is not None:
    setv(to_object, ['triggerTokens'], getv(from_object, ['trigger_tokens']))

  if getv(from_object, ['sliding_window']) is not None:
    setv(
        to_object,
        ['slidingWindow'],
        _SlidingWindow_to_mldev(
            api_client, getv(from_object, ['sliding_window']), to_object
        ),
    )

  return to_object


def _ContextWindowCompressionConfig_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['trigger_tokens']) is not None:
    setv(to_object, ['triggerTokens'], getv(from_object, ['trigger_tokens']))

  if getv(from_object, ['sliding_window']) is not None:
    setv(
        to_object,
        ['slidingWindow'],
        _SlidingWindow_to_vertex(
            api_client, getv(from_object, ['sliding_window']), to_object
        ),
    )

  return to_object


def _LiveConnectConfig_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['generation_config']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig'],
        getv(from_object, ['generation_config']),
    )

  if getv(from_object, ['response_modalities']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'responseModalities'],
        getv(from_object, ['response_modalities']),
    )

  if getv(from_object, ['temperature']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'temperature'],
        getv(from_object, ['temperature']),
    )

  if getv(from_object, ['top_p']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'topP'],
        getv(from_object, ['top_p']),
    )

  if getv(from_object, ['top_k']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'topK'],
        getv(from_object, ['top_k']),
    )

  if getv(from_object, ['max_output_tokens']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'maxOutputTokens'],
        getv(from_object, ['max_output_tokens']),
    )

  if getv(from_object, ['media_resolution']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'mediaResolution'],
        getv(from_object, ['media_resolution']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'seed'],
        getv(from_object, ['seed']),
    )

  if getv(from_object, ['speech_config']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'speechConfig'],
        getv(from_object, ['speech_config']),
    )

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        parent_object,
        ['setup', 'systemInstruction'],
        _Content_to_mldev(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        parent_object,
        ['setup', 'tools'],
        [
            _Tool_to_mldev(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['session_resumption']) is not None:
    setv(
        parent_object,
        ['setup', 'sessionResumption'],
        _SessionResumptionConfig_to_mldev(
            api_client, getv(from_object, ['session_resumption']), to_object
        ),
    )

  if getv(from_object, ['input_audio_transcription']) is not None:
    raise ValueError(
        'input_audio_transcription parameter is not supported in Gemini API.'
    )

  if getv(from_object, ['output_audio_transcription']) is not None:
    setv(
        parent_object,
        ['setup', 'outputAudioTranscription'],
        _AudioTranscriptionConfig_to_mldev(
            api_client,
            getv(from_object, ['output_audio_transcription']),
            to_object,
        ),
    )

  if getv(from_object, ['realtime_input_config']) is not None:
    setv(
        parent_object,
        ['setup', 'realtimeInputConfig'],
        _RealtimeInputConfig_to_mldev(
            api_client, getv(from_object, ['realtime_input_config']), to_object
        ),
    )

  if getv(from_object, ['context_window_compression']) is not None:
    setv(
        parent_object,
        ['setup', 'contextWindowCompression'],
        _ContextWindowCompressionConfig_to_mldev(
            api_client,
            getv(from_object, ['context_window_compression']),
            to_object,
        ),
    )

  return to_object


def _LiveConnectConfig_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['generation_config']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig'],
        getv(from_object, ['generation_config']),
    )

  if getv(from_object, ['response_modalities']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'responseModalities'],
        getv(from_object, ['response_modalities']),
    )

  if getv(from_object, ['temperature']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'temperature'],
        getv(from_object, ['temperature']),
    )

  if getv(from_object, ['top_p']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'topP'],
        getv(from_object, ['top_p']),
    )

  if getv(from_object, ['top_k']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'topK'],
        getv(from_object, ['top_k']),
    )

  if getv(from_object, ['max_output_tokens']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'maxOutputTokens'],
        getv(from_object, ['max_output_tokens']),
    )

  if getv(from_object, ['media_resolution']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'mediaResolution'],
        getv(from_object, ['media_resolution']),
    )

  if getv(from_object, ['seed']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'seed'],
        getv(from_object, ['seed']),
    )

  if getv(from_object, ['speech_config']) is not None:
    setv(
        parent_object,
        ['setup', 'generationConfig', 'speechConfig'],
        getv(from_object, ['speech_config']),
    )

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        parent_object,
        ['setup', 'systemInstruction'],
        _Content_to_vertex(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        parent_object,
        ['setup', 'tools'],
        [
            _Tool_to_vertex(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['session_resumption']) is not None:
    setv(
        parent_object,
        ['setup', 'sessionResumption'],
        _SessionResumptionConfig_to_vertex(
            api_client, getv(from_object, ['session_resumption']), to_object
        ),
    )

  if getv(from_object, ['input_audio_transcription']) is not None:
    setv(
        parent_object,
        ['setup', 'inputAudioTranscription'],
        _AudioTranscriptionConfig_to_vertex(
            api_client,
            getv(from_object, ['input_audio_transcription']),
            to_object,
        ),
    )

  if getv(from_object, ['output_audio_transcription']) is not None:
    setv(
        parent_object,
        ['setup', 'outputAudioTranscription'],
        _AudioTranscriptionConfig_to_vertex(
            api_client,
            getv(from_object, ['output_audio_transcription']),
            to_object,
        ),
    )

  if getv(from_object, ['realtime_input_config']) is not None:
    setv(
        parent_object,
        ['setup', 'realtimeInputConfig'],
        _RealtimeInputConfig_to_vertex(
            api_client, getv(from_object, ['realtime_input_config']), to_object
        ),
    )

  if getv(from_object, ['context_window_compression']) is not None:
    setv(
        parent_object,
        ['setup', 'contextWindowCompression'],
        _ContextWindowCompressionConfig_to_vertex(
            api_client,
            getv(from_object, ['context_window_compression']),
            to_object,
        ),
    )

  return to_object


def _LiveConnectParameters_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['setup', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _LiveConnectConfig_to_mldev(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _LiveConnectParameters_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['model']) is not None:
    setv(
        to_object,
        ['setup', 'model'],
        t.t_model(api_client, getv(from_object, ['model'])),
    )

  if getv(from_object, ['config']) is not None:
    setv(
        to_object,
        ['config'],
        _LiveConnectConfig_to_vertex(
            api_client, getv(from_object, ['config']), to_object
        ),
    )

  return to_object


def _LiveClientSetup_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['model']) is not None:
    setv(to_object, ['model'], getv(from_object, ['model']))

  if getv(from_object, ['generation_config']) is not None:
    setv(
        to_object,
        ['generationConfig'],
        getv(from_object, ['generation_config']),
    )

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        to_object,
        ['systemInstruction'],
        _Content_to_mldev(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        to_object,
        ['tools'],
        [
            _Tool_to_mldev(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['session_resumption']) is not None:
    setv(
        to_object,
        ['sessionResumption'],
        _SessionResumptionConfig_to_mldev(
            api_client, getv(from_object, ['session_resumption']), to_object
        ),
    )

  if getv(from_object, ['context_window_compression']) is not None:
    setv(
        to_object,
        ['contextWindowCompression'],
        _ContextWindowCompressionConfig_to_mldev(
            api_client,
            getv(from_object, ['context_window_compression']),
            to_object,
        ),
    )

  return to_object


def _LiveClientSetup_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['model']) is not None:
    setv(to_object, ['model'], getv(from_object, ['model']))

  if getv(from_object, ['generation_config']) is not None:
    setv(
        to_object,
        ['generationConfig'],
        getv(from_object, ['generation_config']),
    )

  if getv(from_object, ['system_instruction']) is not None:
    setv(
        to_object,
        ['systemInstruction'],
        _Content_to_vertex(
            api_client,
            t.t_content(api_client, getv(from_object, ['system_instruction'])),
            to_object,
        ),
    )

  if getv(from_object, ['tools']) is not None:
    setv(
        to_object,
        ['tools'],
        [
            _Tool_to_vertex(api_client, t.t_tool(api_client, item), to_object)
            for item in t.t_tools(api_client, getv(from_object, ['tools']))
        ],
    )

  if getv(from_object, ['session_resumption']) is not None:
    setv(
        to_object,
        ['sessionResumption'],
        _SessionResumptionConfig_to_vertex(
            api_client, getv(from_object, ['session_resumption']), to_object
        ),
    )

  if getv(from_object, ['context_window_compression']) is not None:
    setv(
        to_object,
        ['contextWindowCompression'],
        _ContextWindowCompressionConfig_to_vertex(
            api_client,
            getv(from_object, ['context_window_compression']),
            to_object,
        ),
    )

  return to_object



def _LiveClientContent_to_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['turns']) is not None:
    setv(
        to_object,
        ['turns'],
        [
            _Content_to_mldev(api_client, item, to_object)
            for item in getv(from_object, ['turns'])
        ],
    )

  if getv(from_object, ['turn_complete']) is not None:
    setv(to_object, ['turnComplete'], getv(from_object, ['turn_complete']))

  return to_object


def _LiveClientContent_to_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict, object],
    parent_object: Optional[dict] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['turns']) is not None:
    setv(
        to_object,
        ['turns'],
        [
            _Content_to_vertex(api_client, item, to_object)
            for item in getv(from_object, ['turns'])
        ],
    )

  if getv(from_object, ['turn_complete']) is not None:
    setv(to_object, ['turnComplete'], getv(from_object, ['turn_complete']))

  return to_object


def _LiveClientToolResponse_to_mldev(
    api_client: BaseApiClient,
    from_object: types.LiveClientToolResponse,
) -> dict:
  tool_response = from_object.model_dump(exclude_none=True, mode='json')
  for response in tool_response.get('function_responses', []):
    if response.get('id') is None:
      raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
  return tool_response


def _LiveClientToolResponse_to_vertex(
    api_client: BaseApiClient,
    from_object: types.LiveClientToolResponse,
) -> dict:
  tool_response = from_object.model_dump(exclude_none=True, mode='json')
  return tool_response


def _LiveServerContent_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['modelTurn']) is not None:
    setv(
        to_object,
        ['model_turn'],
        _Content_from_mldev(
            api_client,
            getv(from_object, ['modelTurn']),
        ),
    )
  if getv(from_object, ['turnComplete']) is not None:
    setv(to_object, ['turn_complete'], getv(from_object, ['turnComplete']))
  if getv(from_object, ['generationComplete']) is not None:
    setv(
        to_object,
        ['generation_complete'],
        getv(from_object, ['generationComplete']),
    )
  if getv(from_object, ['inputTranscription']) is not None:
    setv(
        to_object,
        ['input_transcription'],
        getv(from_object, ['inputTranscription']),
    )
  if getv(from_object, ['outputTranscription']) is not None:
    setv(
        to_object,
        ['output_transcription'],
        getv(from_object, ['outputTranscription']),
    )
  if getv(from_object, ['interrupted']) is not None:
    setv(to_object, ['interrupted'], getv(from_object, ['interrupted']))
  return to_object


def _LiveServerContent_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['modelTurn']) is not None:
    setv(
        to_object,
        ['model_turn'],
        _Content_from_vertex(
            api_client,
            getv(from_object, ['modelTurn']),
        ),
    )
  if getv(from_object, ['turnComplete']) is not None:
    setv(to_object, ['turn_complete'], getv(from_object, ['turnComplete']))
  if getv(from_object, ['generationComplete']) is not None:
    setv(
        to_object,
        ['generation_complete'],
        getv(from_object, ['generationComplete']),
    )
  if getv(from_object, ['inputTranscription']) is not None:
    setv(
        to_object,
        ['input_transcription'],
        getv(from_object, ['inputTranscription']),
    )
  if getv(from_object, ['outputTranscription']) is not None:
    setv(
        to_object,
        ['output_transcription'],
        getv(from_object, ['outputTranscription']),
    )
  if getv(from_object, ['interrupted']) is not None:
    setv(to_object, ['interrupted'], getv(from_object, ['interrupted']))
  return to_object



def _LiveToolCall_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['functionCalls']) is not None:
    setv(
        to_object,
        ['function_calls'],
        getv(from_object, ['functionCalls']),
    )
  return to_object

def _LiveToolCall_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['functionCalls']) is not None:
    setv(
        to_object,
        ['function_calls'],
        getv(from_object, ['functionCalls']),
    )
  return to_object



def _ModalityTokenCount_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: Dict[str, Any] = {}
  if getv(from_object, ['modality']) is not None:
    setv(to_object, ['modality'], getv(from_object, ['modality']))
  if getv(from_object, ['tokenCount']) is not None:
    setv(to_object, ['token_count'], getv(from_object, ['tokenCount']))
  return to_object


def _ModalityTokenCount_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: Dict[str, Any] = {}
  if getv(from_object, ['modality']) is not None:
    setv(to_object, ['modality'], getv(from_object, ['modality']))
  if getv(from_object, ['tokenCount']) is not None:
    setv(to_object, ['token_count'], getv(from_object, ['tokenCount']))
  return to_object


def _UsageMetadata_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['promptTokenCount']) is not None:
    setv(
        to_object,
        ['prompt_token_count'],
        getv(from_object, ['promptTokenCount']),
    )
  if getv(from_object, ['cachedContentTokenCount']) is not None:
    setv(
        to_object,
        ['cached_content_token_count'],
        getv(from_object, ['cachedContentTokenCount']),
    )
  if getv(from_object, ['responseTokenCount']) is not None:
    setv(
        to_object,
        ['response_token_count'],
        getv(from_object, ['responseTokenCount']),
    )
  if getv(from_object, ['toolUsePromptTokenCount']) is not None:
    setv(
        to_object,
        ['tool_use_prompt_token_count'],
        getv(from_object, ['toolUsePromptTokenCount']),
    )
  if getv(from_object, ['thoughtsTokenCount']) is not None:
    setv(
        to_object,
        ['thoughts_token_count'],
        getv(from_object, ['thoughtsTokenCount']),
    )
  if getv(from_object, ['totalTokenCount']) is not None:
    setv(
        to_object,
        ['total_token_count'],
        getv(from_object, ['totalTokenCount']),
    )
  if getv(from_object, ['promptTokensDetails']) is not None:
    setv(
        to_object,
        ['prompt_tokens_details'],
        [
            _ModalityTokenCount_from_mldev(api_client,item)
            for item in getv(from_object, ['promptTokensDetails'])
        ],
    )
  if getv(from_object, ['cacheTokensDetails']) is not None:
    setv(
        to_object,
        ['cache_tokens_details'],
        [
            _ModalityTokenCount_from_mldev(api_client,item)
            for item in getv(from_object, ['cacheTokensDetails'])
        ],
    )
  if getv(from_object, ['responseTokensDetails']) is not None:
    setv(
        to_object,
        ['response_tokens_details'],
        [
            _ModalityTokenCount_from_mldev(api_client,item)
            for item in getv(from_object, ['responseTokensDetails'])
        ],
    )
  if getv(from_object, ['toolUsePromptTokensDetails']) is not None:
    setv(
        to_object,
        ['tool_use_prompt_tokens_details'],
        [
            _ModalityTokenCount_from_mldev(api_client,item)
            for item in getv(from_object, ['toolUsePromptTokensDetails'])
        ],
    )
  return to_object


def _UsageMetadata_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['promptTokenCount']) is not None:
    setv(
        to_object,
        ['prompt_token_count'],
        getv(from_object, ['promptTokenCount']),
    )
  if getv(from_object, ['cachedContentTokenCount']) is not None:
    setv(
        to_object,
        ['cached_content_token_count'],
        getv(from_object, ['cachedContentTokenCount']),
    )
  if getv(from_object, ['candidatesTokenCount']) is not None:
    setv(
        to_object,
        ['response_token_count'],
        getv(from_object, ['candidatesTokenCount']),
    )
  if getv(from_object, ['toolUsePromptTokenCount']) is not None:
    setv(
        to_object,
        ['tool_use_prompt_token_count'],
        getv(from_object, ['toolUsePromptTokenCount']),
    )
  if getv(from_object, ['thoughtsTokenCount']) is not None:
    setv(
        to_object,
        ['thoughts_token_count'],
        getv(from_object, ['thoughtsTokenCount']),
    )
  if getv(from_object, ['totalTokenCount']) is not None:
    setv(
        to_object,
        ['total_token_count'],
        getv(from_object, ['totalTokenCount']),
    )
  if getv(from_object, ['promptTokensDetails']) is not None:
    setv(
        to_object,
        ['prompt_tokens_details'],
        [
            _ModalityTokenCount_from_vertex(api_client,item)
            for item in getv(from_object, ['promptTokensDetails'])
        ],
    )
  if getv(from_object, ['cacheTokensDetails']) is not None:
    setv(
        to_object,
        ['cache_tokens_details'],
        [
            _ModalityTokenCount_from_vertex(api_client,item)
            for item in getv(from_object, ['cacheTokensDetails'])
        ],
    )
  if getv(from_object, ['toolUsePromptTokensDetails']) is not None:
    setv(
        to_object,
        ['tool_use_prompt_tokens_details'],
        [
            _ModalityTokenCount_from_vertex(api_client,item)
            for item in getv(from_object, ['toolUsePromptTokensDetails'])
        ],
    )
  if getv(from_object, ['candidatesTokensDetails']) is not None:
    setv(
        to_object,
        ['response_tokens_details'],
        [
            _ModalityTokenCount_from_vertex(api_client,item)
            for item in getv(from_object, ['candidatesTokensDetails'])
        ],
    )
  if getv(from_object, ['trafficType']) is not None:
    setv(
        to_object,
        ['traffic_type'],
        getv(from_object, ['trafficType']),
    )
  return to_object


def _LiveServerGoAway_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['timeLeft']) is not None:
    setv(to_object, ['time_left'], getv(from_object, ['timeLeft']))

  return to_object


def _LiveServerGoAway_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['timeLeft']) is not None:
    setv(to_object, ['time_left'], getv(from_object, ['timeLeft']))

  return to_object



def _LiveServerSessionResumptionUpdate_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
    parent_object: Optional[dict[str, Any]] = None,
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['newHandle']) is not None:
    setv(to_object, ['new_handle'], getv(from_object, ['newHandle']))

  if getv(from_object, ['resumable']) is not None:
    setv(to_object, ['resumable'], getv(from_object, ['resumable']))

  if getv(from_object, ['lastConsumedClientMessageIndex']) is not None:
    setv(
        to_object,
        ['last_consumed_client_message_index'],
        getv(from_object, ['lastConsumedClientMessageIndex']),
    )

  return to_object





def _LiveServerSessionResumptionUpdate_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> dict:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['newHandle']) is not None:
    setv(to_object, ['new_handle'], getv(from_object, ['newHandle']))

  if getv(from_object, ['resumable']) is not None:
    setv(to_object, ['resumable'], getv(from_object, ['resumable']))

  if getv(from_object, ['lastConsumedClientMessageIndex']) is not None:
    setv(
        to_object,
        ['last_consumed_client_message_index'],
        getv(from_object, ['lastConsumedClientMessageIndex']),
    )

  return to_object



def _LiveServerMessage_from_mldev(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['serverContent']) is not None:
    setv(
        to_object,
        ['server_content'],
        _LiveServerContent_from_mldev(api_client,
            getv(from_object, ['serverContent'])
        ),
    )
  if getv(from_object, ['toolCall']) is not None:
    setv(
        to_object,
        ['tool_call'],
        _LiveToolCall_from_mldev(api_client,getv(from_object, ['toolCall'])),
    )
  if getv(from_object, ['toolCallCancellation']) is not None:
    setv(
        to_object,
        ['tool_call_cancellation'],
        getv(from_object, ['toolCallCancellation']),
    )

  if getv(from_object, ['goAway']) is not None:
    setv(
        to_object,
        ['go_away'],
        _LiveServerGoAway_from_mldev(api_client,
            getv(from_object, ['goAway']), to_object
        ),
    )

  if getv(from_object, ['sessionResumptionUpdate']) is not None:
    setv(
        to_object,
        ['session_resumption_update'],
        _LiveServerSessionResumptionUpdate_from_mldev(api_client,
            getv(from_object, ['sessionResumptionUpdate']),
            to_object,
        ),
    )
  if getv(from_object, ['sessionResumptionUpdate']) is not None:
    setv(
        to_object,
        ['session_resumption_update'],
        _LiveServerSessionResumptionUpdate_from_mldev(api_client,
            getv(from_object, ['sessionResumptionUpdate']),
            to_object,
        ),
    )

  if getv(from_object, ['usageMetadata']) is not None:
    setv(
        to_object,
        ['usage_metadata'],
        _UsageMetadata_from_mldev(api_client,getv(from_object, ['usageMetadata'])),
    )
  return to_object


def _LiveServerMessage_from_vertex(
    api_client: BaseApiClient,
    from_object: Union[dict[str, Any], object],
) -> Dict[str, Any]:
  to_object: dict[str, Any] = {}
  if getv(from_object, ['serverContent']) is not None:
    setv(
        to_object,
        ['server_content'],
        _LiveServerContent_from_vertex(api_client,
            getv(from_object, ['serverContent'])
        ),
    )
  if getv(from_object, ['toolCall']) is not None:
    setv(
        to_object,
        ['tool_call'],
        _LiveToolCall_from_vertex(api_client,getv(from_object, ['toolCall'])),
    )
  if getv(from_object, ['toolCallCancellation']) is not None:
    setv(
        to_object,
        ['tool_call_cancellation'],
        getv(from_object, ['toolCallCancellation']),
    )

  if getv(from_object, ['goAway']) is not None:
    setv(
        to_object,
        ['go_away'],
        _LiveServerGoAway_from_vertex(api_client,
            getv(from_object, ['goAway'])
        ),
    )

  if getv(from_object, ['sessionResumptionUpdate']) is not None:
    setv(
        to_object,
        ['session_resumption_update'],
        _LiveServerSessionResumptionUpdate_from_vertex(api_client,
            getv(from_object, ['sessionResumptionUpdate']),
        ),
    )

  if getv(from_object, ['usageMetadata']) is not None:
    setv(
        to_object,
        ['usage_metadata'],
        _UsageMetadata_from_vertex(api_client,getv(from_object, ['usageMetadata'])),
    )
  return to_object
