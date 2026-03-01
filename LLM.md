# Google GenAI Python Library API

## Module: google.genai.client

### Class: AsyncClient
`from google.genai.client import AsyncClient`
Client for making asynchronous (non-blocking) requests.

#### Methods:
- `__init__(api_client)` - No description
- `models()` - No description
- `tunings()` - No description
- `caches()` - No description
- `batches()` - No description
- `chats()` - No description
- `files()` - No description
- `live()` - No description
- `auth_tokens()` - No description
- `operations()` - No description

### Class: DebugConfig
`from google.genai.client import DebugConfig`
Configuration options that change client network behavior when testing.

### Class: Client
`from google.genai.client import Client`
Client for making synchronous requests.

#### Methods:
- `__init__()` - Initializes the client.
- `_get_api_client(vertexai, api_key, credentials, project, location, debug_config, http_options)` - No description
- `chats()` - No description
- `aio()` - No description
- `models()` - No description
- `tunings()` - No description
- `caches()` - No description
- `batches()` - No description
- `files()` - No description
- `auth_tokens()` - No description
- `operations()` - No description
- `vertexai()` - Returns whether the client is using the Vertex AI API.

## Module: google.genai.models

### Class: Models
`from google.genai.models import Models`
No description

#### Methods:
- `_generate_content()` - No description
- `_generate_content_stream()` - No description
- `embed_content()` - Calculates embeddings for the given contents. Only text is supported.
- `_generate_images()` - Generates images based on a text description and configuration.
- `_edit_image()` - Edits an image based on a text description and configuration.
- `_upscale_image()` - Upscales an image.
- `get()` - No description
- `_list()` - No description
- `update()` - No description
- `delete()` - No description
- `count_tokens()` - Counts the number of tokens in the given content.
- `compute_tokens()` - Given a list of contents, returns a corresponding TokensInfo containing the
- `_generate_videos()` - Generates videos based on an input (text, image, or video) and configuration.
- `generate_content()` - Makes an API request to generate content using a model.
- `generate_content_stream()` - Makes an API request to generate content using a model and yields the model's response in chunks.
- `generate_images()` - Generates images based on a text description and configuration.
- `edit_image()` - Edits an image based on a text description and configuration.
- `upscale_image()` - Makes an API request to upscale a provided image.
- `generate_videos()` - Generates videos based on an input (text, image, or video) and configuration.
- `list()` - Makes an API request to list the available models.

### Class: AsyncModels
`from google.genai.models import AsyncModels`
No description

### Function: _VideoMetadata_to_mldev
`from google.genai.models import _VideoMetadata_to_mldev`
No description

### Function: _Blob_to_mldev
`from google.genai.models import _Blob_to_mldev`
No description

### Function: _FileData_to_mldev
`from google.genai.models import _FileData_to_mldev`
No description

### Function: _Part_to_mldev
`from google.genai.models import _Part_to_mldev`
No description

### Function: _Content_to_mldev
`from google.genai.models import _Content_to_mldev`
No description

### Function: _Schema_to_mldev
`from google.genai.models import _Schema_to_mldev`
No description

### Function: _SafetySetting_to_mldev
`from google.genai.models import _SafetySetting_to_mldev`
No description

### Function: _FunctionDeclaration_to_mldev
`from google.genai.models import _FunctionDeclaration_to_mldev`
No description

### Function: _Interval_to_mldev
`from google.genai.models import _Interval_to_mldev`
No description

### Function: _GoogleSearch_to_mldev
`from google.genai.models import _GoogleSearch_to_mldev`
No description

### Function: _DynamicRetrievalConfig_to_mldev
`from google.genai.models import _DynamicRetrievalConfig_to_mldev`
No description

### Function: _GoogleSearchRetrieval_to_mldev
`from google.genai.models import _GoogleSearchRetrieval_to_mldev`
No description

### Function: _UrlContext_to_mldev
`from google.genai.models import _UrlContext_to_mldev`
No description

### Function: _Tool_to_mldev
`from google.genai.models import _Tool_to_mldev`
No description

### Function: _FunctionCallingConfig_to_mldev
`from google.genai.models import _FunctionCallingConfig_to_mldev`
No description

### Function: _LatLng_to_mldev
`from google.genai.models import _LatLng_to_mldev`
No description

### Function: _RetrievalConfig_to_mldev
`from google.genai.models import _RetrievalConfig_to_mldev`
No description

### Function: _ToolConfig_to_mldev
`from google.genai.models import _ToolConfig_to_mldev`
No description

### Function: _PrebuiltVoiceConfig_to_mldev
`from google.genai.models import _PrebuiltVoiceConfig_to_mldev`
No description

### Function: _VoiceConfig_to_mldev
`from google.genai.models import _VoiceConfig_to_mldev`
No description

### Function: _SpeakerVoiceConfig_to_mldev
`from google.genai.models import _SpeakerVoiceConfig_to_mldev`
No description

### Function: _MultiSpeakerVoiceConfig_to_mldev
`from google.genai.models import _MultiSpeakerVoiceConfig_to_mldev`
No description

### Function: _SpeechConfig_to_mldev
`from google.genai.models import _SpeechConfig_to_mldev`
No description

### Function: _ThinkingConfig_to_mldev
`from google.genai.models import _ThinkingConfig_to_mldev`
No description

### Function: _GenerateContentConfig_to_mldev
`from google.genai.models import _GenerateContentConfig_to_mldev`
No description

### Function: _GenerateContentParameters_to_mldev
`from google.genai.models import _GenerateContentParameters_to_mldev`
No description

### Function: _EmbedContentConfig_to_mldev
`from google.genai.models import _EmbedContentConfig_to_mldev`
No description

### Function: _EmbedContentParameters_to_mldev
`from google.genai.models import _EmbedContentParameters_to_mldev`
No description

### Function: _GenerateImagesConfig_to_mldev
`from google.genai.models import _GenerateImagesConfig_to_mldev`
No description

### Function: _GenerateImagesParameters_to_mldev
`from google.genai.models import _GenerateImagesParameters_to_mldev`
No description

### Function: _GetModelParameters_to_mldev
`from google.genai.models import _GetModelParameters_to_mldev`
No description

### Function: _ListModelsConfig_to_mldev
`from google.genai.models import _ListModelsConfig_to_mldev`
No description

### Function: _ListModelsParameters_to_mldev
`from google.genai.models import _ListModelsParameters_to_mldev`
No description

### Function: _UpdateModelConfig_to_mldev
`from google.genai.models import _UpdateModelConfig_to_mldev`
No description

### Function: _UpdateModelParameters_to_mldev
`from google.genai.models import _UpdateModelParameters_to_mldev`
No description

### Function: _DeleteModelParameters_to_mldev
`from google.genai.models import _DeleteModelParameters_to_mldev`
No description

### Function: _CountTokensConfig_to_mldev
`from google.genai.models import _CountTokensConfig_to_mldev`
No description

### Function: _CountTokensParameters_to_mldev
`from google.genai.models import _CountTokensParameters_to_mldev`
No description

### Function: _Image_to_mldev
`from google.genai.models import _Image_to_mldev`
No description

### Function: _GenerateVideosSource_to_mldev
`from google.genai.models import _GenerateVideosSource_to_mldev`
No description

### Function: _GenerateVideosConfig_to_mldev
`from google.genai.models import _GenerateVideosConfig_to_mldev`
No description

### Function: _GenerateVideosParameters_to_mldev
`from google.genai.models import _GenerateVideosParameters_to_mldev`
No description

### Function: _VideoMetadata_to_vertex
`from google.genai.models import _VideoMetadata_to_vertex`
No description

### Function: _Blob_to_vertex
`from google.genai.models import _Blob_to_vertex`
No description

### Function: _FileData_to_vertex
`from google.genai.models import _FileData_to_vertex`
No description

### Function: _Part_to_vertex
`from google.genai.models import _Part_to_vertex`
No description

### Function: _Content_to_vertex
`from google.genai.models import _Content_to_vertex`
No description

### Function: _Schema_to_vertex
`from google.genai.models import _Schema_to_vertex`
No description

### Function: _ModelSelectionConfig_to_vertex
`from google.genai.models import _ModelSelectionConfig_to_vertex`
No description

### Function: _SafetySetting_to_vertex
`from google.genai.models import _SafetySetting_to_vertex`
No description

### Function: _FunctionDeclaration_to_vertex
`from google.genai.models import _FunctionDeclaration_to_vertex`
No description

### Function: _Interval_to_vertex
`from google.genai.models import _Interval_to_vertex`
No description

### Function: _GoogleSearch_to_vertex
`from google.genai.models import _GoogleSearch_to_vertex`
No description

### Function: _DynamicRetrievalConfig_to_vertex
`from google.genai.models import _DynamicRetrievalConfig_to_vertex`
No description

### Function: _GoogleSearchRetrieval_to_vertex
`from google.genai.models import _GoogleSearchRetrieval_to_vertex`
No description

### Function: _EnterpriseWebSearch_to_vertex
`from google.genai.models import _EnterpriseWebSearch_to_vertex`
No description

### Function: _ApiKeyConfig_to_vertex
`from google.genai.models import _ApiKeyConfig_to_vertex`
No description

### Function: _AuthConfig_to_vertex
`from google.genai.models import _AuthConfig_to_vertex`
No description

### Function: _GoogleMaps_to_vertex
`from google.genai.models import _GoogleMaps_to_vertex`
No description

### Function: _UrlContext_to_vertex
`from google.genai.models import _UrlContext_to_vertex`
No description

### Function: _Tool_to_vertex
`from google.genai.models import _Tool_to_vertex`
No description

### Function: _FunctionCallingConfig_to_vertex
`from google.genai.models import _FunctionCallingConfig_to_vertex`
No description

### Function: _LatLng_to_vertex
`from google.genai.models import _LatLng_to_vertex`
No description

### Function: _RetrievalConfig_to_vertex
`from google.genai.models import _RetrievalConfig_to_vertex`
No description

### Function: _ToolConfig_to_vertex
`from google.genai.models import _ToolConfig_to_vertex`
No description

### Function: _PrebuiltVoiceConfig_to_vertex
`from google.genai.models import _PrebuiltVoiceConfig_to_vertex`
No description

### Function: _VoiceConfig_to_vertex
`from google.genai.models import _VoiceConfig_to_vertex`
No description

### Function: _SpeechConfig_to_vertex
`from google.genai.models import _SpeechConfig_to_vertex`
No description

### Function: _ThinkingConfig_to_vertex
`from google.genai.models import _ThinkingConfig_to_vertex`
No description

### Function: _GenerateContentConfig_to_vertex
`from google.genai.models import _GenerateContentConfig_to_vertex`
No description

### Function: _GenerateContentParameters_to_vertex
`from google.genai.models import _GenerateContentParameters_to_vertex`
No description

### Function: _EmbedContentConfig_to_vertex
`from google.genai.models import _EmbedContentConfig_to_vertex`
No description

### Function: _EmbedContentParameters_to_vertex
`from google.genai.models import _EmbedContentParameters_to_vertex`
No description

### Function: _GenerateImagesConfig_to_vertex
`from google.genai.models import _GenerateImagesConfig_to_vertex`
No description

### Function: _GenerateImagesParameters_to_vertex
`from google.genai.models import _GenerateImagesParameters_to_vertex`
No description

### Function: _Image_to_vertex
`from google.genai.models import _Image_to_vertex`
No description

### Function: _MaskReferenceConfig_to_vertex
`from google.genai.models import _MaskReferenceConfig_to_vertex`
No description

### Function: _ControlReferenceConfig_to_vertex
`from google.genai.models import _ControlReferenceConfig_to_vertex`
No description

### Function: _StyleReferenceConfig_to_vertex
`from google.genai.models import _StyleReferenceConfig_to_vertex`
No description

### Function: _SubjectReferenceConfig_to_vertex
`from google.genai.models import _SubjectReferenceConfig_to_vertex`
No description

### Function: _ReferenceImageAPI_to_vertex
`from google.genai.models import _ReferenceImageAPI_to_vertex`
No description

### Function: _EditImageConfig_to_vertex
`from google.genai.models import _EditImageConfig_to_vertex`
No description

### Function: _EditImageParameters_to_vertex
`from google.genai.models import _EditImageParameters_to_vertex`
No description

### Function: _UpscaleImageAPIConfig_to_vertex
`from google.genai.models import _UpscaleImageAPIConfig_to_vertex`
No description

### Function: _UpscaleImageAPIParameters_to_vertex
`from google.genai.models import _UpscaleImageAPIParameters_to_vertex`
No description

### Function: _GetModelParameters_to_vertex
`from google.genai.models import _GetModelParameters_to_vertex`
No description

### Function: _ListModelsConfig_to_vertex
`from google.genai.models import _ListModelsConfig_to_vertex`
No description

### Function: _ListModelsParameters_to_vertex
`from google.genai.models import _ListModelsParameters_to_vertex`
No description

### Function: _UpdateModelConfig_to_vertex
`from google.genai.models import _UpdateModelConfig_to_vertex`
No description

### Function: _UpdateModelParameters_to_vertex
`from google.genai.models import _UpdateModelParameters_to_vertex`
No description

### Function: _DeleteModelParameters_to_vertex
`from google.genai.models import _DeleteModelParameters_to_vertex`
No description

### Function: _CountTokensConfig_to_vertex
`from google.genai.models import _CountTokensConfig_to_vertex`
No description

### Function: _CountTokensParameters_to_vertex
`from google.genai.models import _CountTokensParameters_to_vertex`
No description

### Function: _ComputeTokensParameters_to_vertex
`from google.genai.models import _ComputeTokensParameters_to_vertex`
No description

### Function: _Video_to_vertex
`from google.genai.models import _Video_to_vertex`
No description

### Function: _GenerateVideosSource_to_vertex
`from google.genai.models import _GenerateVideosSource_to_vertex`
No description

### Function: _GenerateVideosConfig_to_vertex
`from google.genai.models import _GenerateVideosConfig_to_vertex`
No description

### Function: _GenerateVideosParameters_to_vertex
`from google.genai.models import _GenerateVideosParameters_to_vertex`
No description

### Function: _SafetyFilterLevel_to_mldev_enum_validate
`from google.genai.models import _SafetyFilterLevel_to_mldev_enum_validate`
No description

### Function: _PersonGeneration_to_mldev_enum_validate
`from google.genai.models import _PersonGeneration_to_mldev_enum_validate`
No description

### Function: _Behavior_to_vertex_enum_validate
`from google.genai.models import _Behavior_to_vertex_enum_validate`
No description

### Function: _VideoMetadata_from_mldev
`from google.genai.models import _VideoMetadata_from_mldev`
No description

### Function: _Blob_from_mldev
`from google.genai.models import _Blob_from_mldev`
No description

### Function: _FileData_from_mldev
`from google.genai.models import _FileData_from_mldev`
No description

### Function: _Part_from_mldev
`from google.genai.models import _Part_from_mldev`
No description

### Function: _Content_from_mldev
`from google.genai.models import _Content_from_mldev`
No description

### Function: _CitationMetadata_from_mldev
`from google.genai.models import _CitationMetadata_from_mldev`
No description

### Function: _UrlMetadata_from_mldev
`from google.genai.models import _UrlMetadata_from_mldev`
No description

### Function: _UrlContextMetadata_from_mldev
`from google.genai.models import _UrlContextMetadata_from_mldev`
No description

### Function: _Candidate_from_mldev
`from google.genai.models import _Candidate_from_mldev`
No description

### Function: _GenerateContentResponse_from_mldev
`from google.genai.models import _GenerateContentResponse_from_mldev`
No description

### Function: _ContentEmbedding_from_mldev
`from google.genai.models import _ContentEmbedding_from_mldev`
No description

### Function: _EmbedContentMetadata_from_mldev
`from google.genai.models import _EmbedContentMetadata_from_mldev`
No description

### Function: _EmbedContentResponse_from_mldev
`from google.genai.models import _EmbedContentResponse_from_mldev`
No description

### Function: _Image_from_mldev
`from google.genai.models import _Image_from_mldev`
No description

### Function: _SafetyAttributes_from_mldev
`from google.genai.models import _SafetyAttributes_from_mldev`
No description

### Function: _GeneratedImage_from_mldev
`from google.genai.models import _GeneratedImage_from_mldev`
No description

### Function: _GenerateImagesResponse_from_mldev
`from google.genai.models import _GenerateImagesResponse_from_mldev`
No description

### Function: _TunedModelInfo_from_mldev
`from google.genai.models import _TunedModelInfo_from_mldev`
No description

### Function: _Model_from_mldev
`from google.genai.models import _Model_from_mldev`
No description

### Function: _ListModelsResponse_from_mldev
`from google.genai.models import _ListModelsResponse_from_mldev`
No description

### Function: _DeleteModelResponse_from_mldev
`from google.genai.models import _DeleteModelResponse_from_mldev`
No description

### Function: _CountTokensResponse_from_mldev
`from google.genai.models import _CountTokensResponse_from_mldev`
No description

### Function: _Video_from_mldev
`from google.genai.models import _Video_from_mldev`
No description

### Function: _GeneratedVideo_from_mldev
`from google.genai.models import _GeneratedVideo_from_mldev`
No description

### Function: _GenerateVideosResponse_from_mldev
`from google.genai.models import _GenerateVideosResponse_from_mldev`
No description

### Function: _GenerateVideosOperation_from_mldev
`from google.genai.models import _GenerateVideosOperation_from_mldev`
No description

### Function: _VideoMetadata_from_vertex
`from google.genai.models import _VideoMetadata_from_vertex`
No description

### Function: _Blob_from_vertex
`from google.genai.models import _Blob_from_vertex`
No description

### Function: _FileData_from_vertex
`from google.genai.models import _FileData_from_vertex`
No description

### Function: _Part_from_vertex
`from google.genai.models import _Part_from_vertex`
No description

### Function: _Content_from_vertex
`from google.genai.models import _Content_from_vertex`
No description

### Function: _CitationMetadata_from_vertex
`from google.genai.models import _CitationMetadata_from_vertex`
No description

### Function: _UrlMetadata_from_vertex
`from google.genai.models import _UrlMetadata_from_vertex`
No description

### Function: _UrlContextMetadata_from_vertex
`from google.genai.models import _UrlContextMetadata_from_vertex`
No description

### Function: _Candidate_from_vertex
`from google.genai.models import _Candidate_from_vertex`
No description

### Function: _GenerateContentResponse_from_vertex
`from google.genai.models import _GenerateContentResponse_from_vertex`
No description

### Function: _ContentEmbeddingStatistics_from_vertex
`from google.genai.models import _ContentEmbeddingStatistics_from_vertex`
No description

### Function: _ContentEmbedding_from_vertex
`from google.genai.models import _ContentEmbedding_from_vertex`
No description

### Function: _EmbedContentMetadata_from_vertex
`from google.genai.models import _EmbedContentMetadata_from_vertex`
No description

### Function: _EmbedContentResponse_from_vertex
`from google.genai.models import _EmbedContentResponse_from_vertex`
No description

### Function: _Image_from_vertex
`from google.genai.models import _Image_from_vertex`
No description

### Function: _SafetyAttributes_from_vertex
`from google.genai.models import _SafetyAttributes_from_vertex`
No description

### Function: _GeneratedImage_from_vertex
`from google.genai.models import _GeneratedImage_from_vertex`
No description

### Function: _GenerateImagesResponse_from_vertex
`from google.genai.models import _GenerateImagesResponse_from_vertex`
No description

### Function: _EditImageResponse_from_vertex
`from google.genai.models import _EditImageResponse_from_vertex`
No description

### Function: _UpscaleImageResponse_from_vertex
`from google.genai.models import _UpscaleImageResponse_from_vertex`
No description

### Function: _Endpoint_from_vertex
`from google.genai.models import _Endpoint_from_vertex`
No description

### Function: _TunedModelInfo_from_vertex
`from google.genai.models import _TunedModelInfo_from_vertex`
No description

### Function: _Checkpoint_from_vertex
`from google.genai.models import _Checkpoint_from_vertex`
No description

### Function: _Model_from_vertex
`from google.genai.models import _Model_from_vertex`
No description

### Function: _ListModelsResponse_from_vertex
`from google.genai.models import _ListModelsResponse_from_vertex`
No description

### Function: _DeleteModelResponse_from_vertex
`from google.genai.models import _DeleteModelResponse_from_vertex`
No description

### Function: _CountTokensResponse_from_vertex
`from google.genai.models import _CountTokensResponse_from_vertex`
No description

### Function: _ComputeTokensResponse_from_vertex
`from google.genai.models import _ComputeTokensResponse_from_vertex`
No description

### Function: _Video_from_vertex
`from google.genai.models import _Video_from_vertex`
No description

### Function: _GeneratedVideo_from_vertex
`from google.genai.models import _GeneratedVideo_from_vertex`
No description

### Function: _GenerateVideosResponse_from_vertex
`from google.genai.models import _GenerateVideosResponse_from_vertex`
No description

### Function: _GenerateVideosOperation_from_vertex
`from google.genai.models import _GenerateVideosOperation_from_vertex`
No description

## Module: google.genai.chats

### Class: _BaseChat
`from google.genai.chats import _BaseChat`
Base chat session.

#### Methods:
- `__init__()` - No description
- `record_history(user_input, model_output, automatic_function_calling_history, is_valid)` - Records the chat history.
- `get_history(curated)` - Returns the chat history.

### Class: Chat
`from google.genai.chats import Chat`
Chat session.

#### Methods:
- `__init__()` - No description
- `send_message(message, config)` - Sends the conversation history with the additional message and returns the model's response.
- `send_message_stream(message, config)` - Sends the conversation history with the additional message and yields the model's response in chunks.

### Class: Chats
`from google.genai.chats import Chats`
A util class to create chat sessions.

#### Methods:
- `__init__(modules)` - No description
- `create()` - Creates a new chat session.

### Class: AsyncChat
`from google.genai.chats import AsyncChat`
Async chat session.

#### Methods:
- `__init__()` - No description

### Class: AsyncChats
`from google.genai.chats import AsyncChats`
A util class to create async chat sessions.

#### Methods:
- `__init__(modules)` - No description
- `create()` - Creates a new chat session.

### Function: _validate_content
`from google.genai.chats import _validate_content`
No description

### Function: _validate_contents
`from google.genai.chats import _validate_contents`
No description

### Function: _validate_response
`from google.genai.chats import _validate_response`
No description

### Function: _extract_curated_history
`from google.genai.chats import _extract_curated_history`
Extracts the curated (valid) history from a comprehensive history.

### Function: _is_part_type
`from google.genai.chats import _is_part_type`
No description

## Module: google.genai.batches

### Class: Batches
`from google.genai.batches import Batches`
No description

#### Methods:
- `_create()` - No description
- `get()` - Gets a batch job.
- `cancel()` - Cancels a batch job.
- `_list()` - No description
- `delete()` - Deletes a batch job.
- `create()` - Creates a batch job.
- `list()` - Lists batch jobs.

### Class: AsyncBatches
`from google.genai.batches import AsyncBatches`
No description

### Function: _VideoMetadata_to_mldev
`from google.genai.batches import _VideoMetadata_to_mldev`
No description

### Function: _Blob_to_mldev
`from google.genai.batches import _Blob_to_mldev`
No description

### Function: _FileData_to_mldev
`from google.genai.batches import _FileData_to_mldev`
No description

### Function: _Part_to_mldev
`from google.genai.batches import _Part_to_mldev`
No description

### Function: _Content_to_mldev
`from google.genai.batches import _Content_to_mldev`
No description

### Function: _Schema_to_mldev
`from google.genai.batches import _Schema_to_mldev`
No description

### Function: _SafetySetting_to_mldev
`from google.genai.batches import _SafetySetting_to_mldev`
No description

### Function: _FunctionDeclaration_to_mldev
`from google.genai.batches import _FunctionDeclaration_to_mldev`
No description

### Function: _Interval_to_mldev
`from google.genai.batches import _Interval_to_mldev`
No description

### Function: _GoogleSearch_to_mldev
`from google.genai.batches import _GoogleSearch_to_mldev`
No description

### Function: _DynamicRetrievalConfig_to_mldev
`from google.genai.batches import _DynamicRetrievalConfig_to_mldev`
No description

### Function: _GoogleSearchRetrieval_to_mldev
`from google.genai.batches import _GoogleSearchRetrieval_to_mldev`
No description

### Function: _UrlContext_to_mldev
`from google.genai.batches import _UrlContext_to_mldev`
No description

### Function: _Tool_to_mldev
`from google.genai.batches import _Tool_to_mldev`
No description

### Function: _FunctionCallingConfig_to_mldev
`from google.genai.batches import _FunctionCallingConfig_to_mldev`
No description

### Function: _LatLng_to_mldev
`from google.genai.batches import _LatLng_to_mldev`
No description

### Function: _RetrievalConfig_to_mldev
`from google.genai.batches import _RetrievalConfig_to_mldev`
No description

### Function: _ToolConfig_to_mldev
`from google.genai.batches import _ToolConfig_to_mldev`
No description

### Function: _PrebuiltVoiceConfig_to_mldev
`from google.genai.batches import _PrebuiltVoiceConfig_to_mldev`
No description

### Function: _VoiceConfig_to_mldev
`from google.genai.batches import _VoiceConfig_to_mldev`
No description

### Function: _SpeakerVoiceConfig_to_mldev
`from google.genai.batches import _SpeakerVoiceConfig_to_mldev`
No description

### Function: _MultiSpeakerVoiceConfig_to_mldev
`from google.genai.batches import _MultiSpeakerVoiceConfig_to_mldev`
No description

### Function: _SpeechConfig_to_mldev
`from google.genai.batches import _SpeechConfig_to_mldev`
No description

### Function: _ThinkingConfig_to_mldev
`from google.genai.batches import _ThinkingConfig_to_mldev`
No description

### Function: _GenerateContentConfig_to_mldev
`from google.genai.batches import _GenerateContentConfig_to_mldev`
No description

### Function: _InlinedRequest_to_mldev
`from google.genai.batches import _InlinedRequest_to_mldev`
No description

### Function: _BatchJobSource_to_mldev
`from google.genai.batches import _BatchJobSource_to_mldev`
No description

### Function: _CreateBatchJobConfig_to_mldev
`from google.genai.batches import _CreateBatchJobConfig_to_mldev`
No description

### Function: _CreateBatchJobParameters_to_mldev
`from google.genai.batches import _CreateBatchJobParameters_to_mldev`
No description

### Function: _GetBatchJobParameters_to_mldev
`from google.genai.batches import _GetBatchJobParameters_to_mldev`
No description

### Function: _CancelBatchJobParameters_to_mldev
`from google.genai.batches import _CancelBatchJobParameters_to_mldev`
No description

### Function: _ListBatchJobsConfig_to_mldev
`from google.genai.batches import _ListBatchJobsConfig_to_mldev`
No description

### Function: _ListBatchJobsParameters_to_mldev
`from google.genai.batches import _ListBatchJobsParameters_to_mldev`
No description

### Function: _DeleteBatchJobParameters_to_mldev
`from google.genai.batches import _DeleteBatchJobParameters_to_mldev`
No description

### Function: _BatchJobSource_to_vertex
`from google.genai.batches import _BatchJobSource_to_vertex`
No description

### Function: _BatchJobDestination_to_vertex
`from google.genai.batches import _BatchJobDestination_to_vertex`
No description

### Function: _CreateBatchJobConfig_to_vertex
`from google.genai.batches import _CreateBatchJobConfig_to_vertex`
No description

### Function: _CreateBatchJobParameters_to_vertex
`from google.genai.batches import _CreateBatchJobParameters_to_vertex`
No description

### Function: _GetBatchJobParameters_to_vertex
`from google.genai.batches import _GetBatchJobParameters_to_vertex`
No description

### Function: _CancelBatchJobParameters_to_vertex
`from google.genai.batches import _CancelBatchJobParameters_to_vertex`
No description

### Function: _ListBatchJobsConfig_to_vertex
`from google.genai.batches import _ListBatchJobsConfig_to_vertex`
No description

### Function: _ListBatchJobsParameters_to_vertex
`from google.genai.batches import _ListBatchJobsParameters_to_vertex`
No description

### Function: _DeleteBatchJobParameters_to_vertex
`from google.genai.batches import _DeleteBatchJobParameters_to_vertex`
No description

### Function: _VideoMetadata_from_mldev
`from google.genai.batches import _VideoMetadata_from_mldev`
No description

### Function: _Blob_from_mldev
`from google.genai.batches import _Blob_from_mldev`
No description

### Function: _FileData_from_mldev
`from google.genai.batches import _FileData_from_mldev`
No description

### Function: _Part_from_mldev
`from google.genai.batches import _Part_from_mldev`
No description

### Function: _Content_from_mldev
`from google.genai.batches import _Content_from_mldev`
No description

### Function: _CitationMetadata_from_mldev
`from google.genai.batches import _CitationMetadata_from_mldev`
No description

### Function: _UrlMetadata_from_mldev
`from google.genai.batches import _UrlMetadata_from_mldev`
No description

### Function: _UrlContextMetadata_from_mldev
`from google.genai.batches import _UrlContextMetadata_from_mldev`
No description

### Function: _Candidate_from_mldev
`from google.genai.batches import _Candidate_from_mldev`
No description

### Function: _GenerateContentResponse_from_mldev
`from google.genai.batches import _GenerateContentResponse_from_mldev`
No description

### Function: _JobError_from_mldev
`from google.genai.batches import _JobError_from_mldev`
No description

### Function: _InlinedResponse_from_mldev
`from google.genai.batches import _InlinedResponse_from_mldev`
No description

### Function: _BatchJobDestination_from_mldev
`from google.genai.batches import _BatchJobDestination_from_mldev`
No description

### Function: _BatchJob_from_mldev
`from google.genai.batches import _BatchJob_from_mldev`
No description

### Function: _ListBatchJobsResponse_from_mldev
`from google.genai.batches import _ListBatchJobsResponse_from_mldev`
No description

### Function: _DeleteResourceJob_from_mldev
`from google.genai.batches import _DeleteResourceJob_from_mldev`
No description

### Function: _JobError_from_vertex
`from google.genai.batches import _JobError_from_vertex`
No description

### Function: _BatchJobSource_from_vertex
`from google.genai.batches import _BatchJobSource_from_vertex`
No description

### Function: _BatchJobDestination_from_vertex
`from google.genai.batches import _BatchJobDestination_from_vertex`
No description

### Function: _BatchJob_from_vertex
`from google.genai.batches import _BatchJob_from_vertex`
No description

### Function: _ListBatchJobsResponse_from_vertex
`from google.genai.batches import _ListBatchJobsResponse_from_vertex`
No description

### Function: _DeleteResourceJob_from_vertex
`from google.genai.batches import _DeleteResourceJob_from_vertex`
No description

## Module: google.genai.caches

### Class: Caches
`from google.genai.caches import Caches`
No description

#### Methods:
- `create()` - Creates a cached contents resource.
- `get()` - Gets cached content configurations.
- `delete()` - Deletes cached content.
- `update()` - Updates cached content configurations.
- `_list()` - Lists cached content configurations.
- `list()` - No description

### Class: AsyncCaches
`from google.genai.caches import AsyncCaches`
No description

### Function: _VideoMetadata_to_mldev
`from google.genai.caches import _VideoMetadata_to_mldev`
No description

### Function: _Blob_to_mldev
`from google.genai.caches import _Blob_to_mldev`
No description

### Function: _FileData_to_mldev
`from google.genai.caches import _FileData_to_mldev`
No description

### Function: _Part_to_mldev
`from google.genai.caches import _Part_to_mldev`
No description

### Function: _Content_to_mldev
`from google.genai.caches import _Content_to_mldev`
No description

### Function: _FunctionDeclaration_to_mldev
`from google.genai.caches import _FunctionDeclaration_to_mldev`
No description

### Function: _Interval_to_mldev
`from google.genai.caches import _Interval_to_mldev`
No description

### Function: _GoogleSearch_to_mldev
`from google.genai.caches import _GoogleSearch_to_mldev`
No description

### Function: _DynamicRetrievalConfig_to_mldev
`from google.genai.caches import _DynamicRetrievalConfig_to_mldev`
No description

### Function: _GoogleSearchRetrieval_to_mldev
`from google.genai.caches import _GoogleSearchRetrieval_to_mldev`
No description

### Function: _UrlContext_to_mldev
`from google.genai.caches import _UrlContext_to_mldev`
No description

### Function: _Tool_to_mldev
`from google.genai.caches import _Tool_to_mldev`
No description

### Function: _FunctionCallingConfig_to_mldev
`from google.genai.caches import _FunctionCallingConfig_to_mldev`
No description

### Function: _LatLng_to_mldev
`from google.genai.caches import _LatLng_to_mldev`
No description

### Function: _RetrievalConfig_to_mldev
`from google.genai.caches import _RetrievalConfig_to_mldev`
No description

### Function: _ToolConfig_to_mldev
`from google.genai.caches import _ToolConfig_to_mldev`
No description

### Function: _CreateCachedContentConfig_to_mldev
`from google.genai.caches import _CreateCachedContentConfig_to_mldev`
No description

### Function: _CreateCachedContentParameters_to_mldev
`from google.genai.caches import _CreateCachedContentParameters_to_mldev`
No description

### Function: _GetCachedContentParameters_to_mldev
`from google.genai.caches import _GetCachedContentParameters_to_mldev`
No description

### Function: _DeleteCachedContentParameters_to_mldev
`from google.genai.caches import _DeleteCachedContentParameters_to_mldev`
No description

### Function: _UpdateCachedContentConfig_to_mldev
`from google.genai.caches import _UpdateCachedContentConfig_to_mldev`
No description

### Function: _UpdateCachedContentParameters_to_mldev
`from google.genai.caches import _UpdateCachedContentParameters_to_mldev`
No description

### Function: _ListCachedContentsConfig_to_mldev
`from google.genai.caches import _ListCachedContentsConfig_to_mldev`
No description

### Function: _ListCachedContentsParameters_to_mldev
`from google.genai.caches import _ListCachedContentsParameters_to_mldev`
No description

### Function: _VideoMetadata_to_vertex
`from google.genai.caches import _VideoMetadata_to_vertex`
No description

### Function: _Blob_to_vertex
`from google.genai.caches import _Blob_to_vertex`
No description

### Function: _FileData_to_vertex
`from google.genai.caches import _FileData_to_vertex`
No description

### Function: _Part_to_vertex
`from google.genai.caches import _Part_to_vertex`
No description

### Function: _Content_to_vertex
`from google.genai.caches import _Content_to_vertex`
No description

### Function: _FunctionDeclaration_to_vertex
`from google.genai.caches import _FunctionDeclaration_to_vertex`
No description

### Function: _Interval_to_vertex
`from google.genai.caches import _Interval_to_vertex`
No description

### Function: _GoogleSearch_to_vertex
`from google.genai.caches import _GoogleSearch_to_vertex`
No description

### Function: _DynamicRetrievalConfig_to_vertex
`from google.genai.caches import _DynamicRetrievalConfig_to_vertex`
No description

### Function: _GoogleSearchRetrieval_to_vertex
`from google.genai.caches import _GoogleSearchRetrieval_to_vertex`
No description

### Function: _EnterpriseWebSearch_to_vertex
`from google.genai.caches import _EnterpriseWebSearch_to_vertex`
No description

### Function: _ApiKeyConfig_to_vertex
`from google.genai.caches import _ApiKeyConfig_to_vertex`
No description

### Function: _AuthConfig_to_vertex
`from google.genai.caches import _AuthConfig_to_vertex`
No description

### Function: _GoogleMaps_to_vertex
`from google.genai.caches import _GoogleMaps_to_vertex`
No description

### Function: _UrlContext_to_vertex
`from google.genai.caches import _UrlContext_to_vertex`
No description

### Function: _Tool_to_vertex
`from google.genai.caches import _Tool_to_vertex`
No description

### Function: _FunctionCallingConfig_to_vertex
`from google.genai.caches import _FunctionCallingConfig_to_vertex`
No description

### Function: _LatLng_to_vertex
`from google.genai.caches import _LatLng_to_vertex`
No description

### Function: _RetrievalConfig_to_vertex
`from google.genai.caches import _RetrievalConfig_to_vertex`
No description

### Function: _ToolConfig_to_vertex
`from google.genai.caches import _ToolConfig_to_vertex`
No description

### Function: _CreateCachedContentConfig_to_vertex
`from google.genai.caches import _CreateCachedContentConfig_to_vertex`
No description

### Function: _CreateCachedContentParameters_to_vertex
`from google.genai.caches import _CreateCachedContentParameters_to_vertex`
No description

### Function: _GetCachedContentParameters_to_vertex
`from google.genai.caches import _GetCachedContentParameters_to_vertex`
No description

### Function: _DeleteCachedContentParameters_to_vertex
`from google.genai.caches import _DeleteCachedContentParameters_to_vertex`
No description

### Function: _UpdateCachedContentConfig_to_vertex
`from google.genai.caches import _UpdateCachedContentConfig_to_vertex`
No description

### Function: _UpdateCachedContentParameters_to_vertex
`from google.genai.caches import _UpdateCachedContentParameters_to_vertex`
No description

### Function: _ListCachedContentsConfig_to_vertex
`from google.genai.caches import _ListCachedContentsConfig_to_vertex`
No description

### Function: _ListCachedContentsParameters_to_vertex
`from google.genai.caches import _ListCachedContentsParameters_to_vertex`
No description

### Function: _Behavior_to_vertex_enum_validate
`from google.genai.caches import _Behavior_to_vertex_enum_validate`
No description

### Function: _CachedContent_from_mldev
`from google.genai.caches import _CachedContent_from_mldev`
No description

### Function: _DeleteCachedContentResponse_from_mldev
`from google.genai.caches import _DeleteCachedContentResponse_from_mldev`
No description

### Function: _ListCachedContentsResponse_from_mldev
`from google.genai.caches import _ListCachedContentsResponse_from_mldev`
No description

### Function: _CachedContent_from_vertex
`from google.genai.caches import _CachedContent_from_vertex`
No description

### Function: _DeleteCachedContentResponse_from_vertex
`from google.genai.caches import _DeleteCachedContentResponse_from_vertex`
No description

### Function: _ListCachedContentsResponse_from_vertex
`from google.genai.caches import _ListCachedContentsResponse_from_vertex`
No description

## Module: google.genai.files

### Class: Files
`from google.genai.files import Files`
No description

#### Methods:
- `_list()` - Lists all files from the service.
- `_create()` - No description
- `get()` - Retrieves the file information from the service.
- `delete()` - Deletes a remotely stored file.
- `upload()` - Calls the API to upload a file using a supported file service.
- `list()` - No description
- `download()` - Downloads a file's data from storage.

### Class: AsyncFiles
`from google.genai.files import AsyncFiles`
No description

### Function: _ListFilesConfig_to_mldev
`from google.genai.files import _ListFilesConfig_to_mldev`
No description

### Function: _ListFilesParameters_to_mldev
`from google.genai.files import _ListFilesParameters_to_mldev`
No description

### Function: _FileStatus_to_mldev
`from google.genai.files import _FileStatus_to_mldev`
No description

### Function: _File_to_mldev
`from google.genai.files import _File_to_mldev`
No description

### Function: _CreateFileParameters_to_mldev
`from google.genai.files import _CreateFileParameters_to_mldev`
No description

### Function: _GetFileParameters_to_mldev
`from google.genai.files import _GetFileParameters_to_mldev`
No description

### Function: _DeleteFileParameters_to_mldev
`from google.genai.files import _DeleteFileParameters_to_mldev`
No description

### Function: _FileStatus_from_mldev
`from google.genai.files import _FileStatus_from_mldev`
No description

### Function: _File_from_mldev
`from google.genai.files import _File_from_mldev`
No description

### Function: _ListFilesResponse_from_mldev
`from google.genai.files import _ListFilesResponse_from_mldev`
No description

### Function: _CreateFileResponse_from_mldev
`from google.genai.files import _CreateFileResponse_from_mldev`
No description

### Function: _DeleteFileResponse_from_mldev
`from google.genai.files import _DeleteFileResponse_from_mldev`
No description

## Module: google.genai.live

### Class: AsyncSession
`from google.genai.live import AsyncSession`
[Preview] AsyncSession.

#### Methods:
- `__init__(api_client, websocket)` - No description
- `_parse_client_message(input, end_of_turn)` - No description

### Class: AsyncLive
`from google.genai.live import AsyncLive`
[Preview] AsyncLive.

#### Methods:
- `__init__(api_client)` - No description
- `music()` - No description

## Module: google.genai.tokens

### Class: Tokens
`from google.genai.tokens import Tokens`
[Experimental] Auth Tokens API client.

#### Methods:
- `create()` - [Experimental] Creates an auth token.

### Class: AsyncTokens
`from google.genai.tokens import AsyncTokens`
[Experimental] Async Auth Tokens API client.

### Function: _get_field_masks
`from google.genai.tokens import _get_field_masks`
Return field_masks

### Function: _convert_bidi_setup_to_token_setup
`from google.genai.tokens import _convert_bidi_setup_to_token_setup`
Converts bidiGenerateContentSetup.

## Module: google.genai.tunings

### Class: Tunings
`from google.genai.tunings import Tunings`
No description

#### Methods:
- `_get()` - Gets a TuningJob.
- `_list()` - Lists `TuningJob` objects.
- `_tune()` - Creates a supervised fine-tuning job and returns the TuningJob object.
- `_tune_mldev()` - Creates a supervised fine-tuning job and returns the TuningJob object.
- `list()` - No description
- `get()` - No description
- `tune()` - No description

### Class: AsyncTunings
`from google.genai.tunings import AsyncTunings`
No description

### Class: _IpythonUtils
`from google.genai.tunings import _IpythonUtils`
Temporary class to hold the IPython related functions.

#### Methods:
- `_get_ipython_shell_name()` - No description
- `is_ipython_available()` - No description
- `_get_styles()` - Returns the HTML style markup to support custom buttons.
- `_parse_resource_name(marker, resource_parts)` - Returns the part after the marker text part.
- `_display_link(text, url, icon)` - Creates and displays the link to open the Vertex resource.
- `display_experiment_button(experiment, project)` - Function to generate a link bound to the Vertex experiment.
- `display_model_tuning_button(tuning_job_resource)` - Function to generate a link bound to the Vertex model tuning job.

### Function: _GetTuningJobParameters_to_mldev
`from google.genai.tunings import _GetTuningJobParameters_to_mldev`
No description

### Function: _ListTuningJobsConfig_to_mldev
`from google.genai.tunings import _ListTuningJobsConfig_to_mldev`
No description

### Function: _ListTuningJobsParameters_to_mldev
`from google.genai.tunings import _ListTuningJobsParameters_to_mldev`
No description

### Function: _TuningExample_to_mldev
`from google.genai.tunings import _TuningExample_to_mldev`
No description

### Function: _TuningDataset_to_mldev
`from google.genai.tunings import _TuningDataset_to_mldev`
No description

### Function: _CreateTuningJobConfig_to_mldev
`from google.genai.tunings import _CreateTuningJobConfig_to_mldev`
No description

### Function: _CreateTuningJobParameters_to_mldev
`from google.genai.tunings import _CreateTuningJobParameters_to_mldev`
No description

### Function: _GetTuningJobParameters_to_vertex
`from google.genai.tunings import _GetTuningJobParameters_to_vertex`
No description

### Function: _ListTuningJobsConfig_to_vertex
`from google.genai.tunings import _ListTuningJobsConfig_to_vertex`
No description

### Function: _ListTuningJobsParameters_to_vertex
`from google.genai.tunings import _ListTuningJobsParameters_to_vertex`
No description

### Function: _TuningDataset_to_vertex
`from google.genai.tunings import _TuningDataset_to_vertex`
No description

### Function: _TuningValidationDataset_to_vertex
`from google.genai.tunings import _TuningValidationDataset_to_vertex`
No description

### Function: _CreateTuningJobConfig_to_vertex
`from google.genai.tunings import _CreateTuningJobConfig_to_vertex`
No description

### Function: _CreateTuningJobParameters_to_vertex
`from google.genai.tunings import _CreateTuningJobParameters_to_vertex`
No description

### Function: _TunedModel_from_mldev
`from google.genai.tunings import _TunedModel_from_mldev`
No description

### Function: _TuningJob_from_mldev
`from google.genai.tunings import _TuningJob_from_mldev`
No description

### Function: _ListTuningJobsResponse_from_mldev
`from google.genai.tunings import _ListTuningJobsResponse_from_mldev`
No description

### Function: _TuningOperation_from_mldev
`from google.genai.tunings import _TuningOperation_from_mldev`
No description

### Function: _TunedModelCheckpoint_from_vertex
`from google.genai.tunings import _TunedModelCheckpoint_from_vertex`
No description

### Function: _TunedModel_from_vertex
`from google.genai.tunings import _TunedModel_from_vertex`
No description

### Function: _TuningJob_from_vertex
`from google.genai.tunings import _TuningJob_from_vertex`
No description

### Function: _ListTuningJobsResponse_from_vertex
`from google.genai.tunings import _ListTuningJobsResponse_from_vertex`
No description

## Module: google.genai.operations

### Class: Operations
`from google.genai.operations import Operations`
No description

#### Methods:
- `_get_videos_operation()` - No description
- `_fetch_predict_videos_operation()` - No description
- `get(operation)` - Gets the status of an operation.

### Class: AsyncOperations
`from google.genai.operations import AsyncOperations`
No description

### Function: _GetOperationParameters_to_mldev
`from google.genai.operations import _GetOperationParameters_to_mldev`
No description

### Function: _GetOperationParameters_to_vertex
`from google.genai.operations import _GetOperationParameters_to_vertex`
No description

### Function: _FetchPredictOperationParameters_to_vertex
`from google.genai.operations import _FetchPredictOperationParameters_to_vertex`
No description
