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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from .._utils import PropertyInfo
from .._models import BaseModel
from .function import Function
from .allowed_tools import AllowedTools

__all__ = [
    "Tool",
    "CodeExecution",
    "URLContext",
    "ComputerUse",
    "MCPServer",
    "GoogleSearch",
    "FileSearch",
    "GoogleMaps",
    "Retrieval",
    "RetrievalExaAISearchConfig",
    "RetrievalParallelAISearchConfig",
    "RetrievalRagStoreConfig",
    "RetrievalRagStoreConfigRagResource",
    "RetrievalRagStoreConfigRagRetrievalConfig",
    "RetrievalRagStoreConfigRagRetrievalConfigFilter",
    "RetrievalRagStoreConfigRagRetrievalConfigHybridSearch",
    "RetrievalRagStoreConfigRagRetrievalConfigRanking",
    "RetrievalVertexAISearchConfig",
]


class CodeExecution(BaseModel):
    """A tool that can be used by the model to execute code."""

    type: Literal["code_execution"]


class URLContext(BaseModel):
    """A tool that can be used by the model to fetch URL context."""

    type: Literal["url_context"]


class ComputerUse(BaseModel):
    """A tool that can be used by the model to interact with the computer."""

    type: Literal["computer_use"]

    enable_prompt_injection_detection: Optional[bool] = None
    """Whether enable the prompt injection detection check on computer-use request."""

    environment: Optional[Literal["browser", "mobile", "desktop"]] = None
    """The environment being operated."""

    excluded_predefined_functions: Optional[List[str]] = None
    """The list of predefined functions that are excluded from the model call."""


class MCPServer(BaseModel):
    """A MCPServer is a server that can be called by the model to perform actions."""

    type: Literal["mcp_server"]

    allowed_tools: Optional[List[AllowedTools]] = None
    """The allowed tools."""

    headers: Optional[Dict[str, str]] = None
    """Optional: Fields for authentication headers, timeouts, etc., if needed."""

    name: Optional[str] = None
    """The name of the MCPServer."""

    url: Optional[str] = None
    """The full URL for the MCPServer endpoint. Example: "https://api.example.com/mcp" """


class GoogleSearch(BaseModel):
    """A tool that can be used by the model to search Google."""

    type: Literal["google_search"]

    search_types: Optional[List[Literal["web_search", "image_search", "enterprise_web_search"]]] = None
    """The types of search grounding to enable."""


class FileSearch(BaseModel):
    """A tool that can be used by the model to search files."""

    type: Literal["file_search"]

    file_search_store_names: Optional[List[str]] = None
    """The file search store names to search."""

    metadata_filter: Optional[str] = None
    """Metadata filter to apply to the semantic retrieval documents and chunks."""

    top_k: Optional[int] = None
    """The number of semantic retrieval chunks to retrieve."""


class GoogleMaps(BaseModel):
    """A tool that can be used by the model to call Google Maps."""

    type: Literal["google_maps"]

    enable_widget: Optional[bool] = None
    """
    Whether to return a widget context token in the tool call result of the
    response.
    """

    latitude: Optional[float] = None
    """The latitude of the user's location."""

    longitude: Optional[float] = None
    """The longitude of the user's location."""


class RetrievalExaAISearchConfig(BaseModel):
    """Used to specify configuration for ExaAISearch."""

    api_key: str
    """Required. The API key for ExaAiSearch."""

    custom_config: Optional[Dict[str, object]] = None
    """Optional.

    This field can be used to pass any parameter from the Exa.ai Search API.
    """


class RetrievalParallelAISearchConfig(BaseModel):
    """Used to specify configuration for ParallelAISearch."""

    api_key: Optional[str] = None
    """Optional. The API key for ParallelAiSearch."""

    custom_config: Optional[Dict[str, object]] = None
    """Optional. Custom configs for ParallelAiSearch."""


class RetrievalRagStoreConfigRagResource(BaseModel):
    """The definition of the Rag resource."""

    rag_corpus: Optional[str] = None
    """Optional. RagCorpora resource name."""

    rag_file_ids: Optional[List[str]] = None
    """Optional.

    rag_file_id. The files should be in the same rag_corpus set in rag_corpus field.
    """


class RetrievalRagStoreConfigRagRetrievalConfigFilter(BaseModel):
    """Optional. Config for filters."""

    metadata_filter: Optional[str] = None
    """Optional. String for metadata filtering."""

    vector_distance_threshold: Optional[float] = None
    """Optional.

    Only returns contexts with vector distance smaller than the threshold.
    """

    vector_similarity_threshold: Optional[float] = None
    """Optional.

    Only returns contexts with vector similarity larger than the threshold.
    """


class RetrievalRagStoreConfigRagRetrievalConfigHybridSearch(BaseModel):
    """Optional. Config for Hybrid Search."""

    alpha: Optional[float] = None
    """Optional.

    Alpha value controls the weight between dense and sparse vector search results.
    """


class RetrievalRagStoreConfigRagRetrievalConfigRanking(BaseModel):
    """Optional. Config for ranking and reranking."""

    ranking_config: Literal["rank_service"]

    api_model_name: Optional[str] = FieldInfo(alias="model_name", default=None)
    """Optional. The model name of the rank service."""


class RetrievalRagStoreConfigRagRetrievalConfig(BaseModel):
    """Optional. The retrieval config for the Rag query."""

    filter: Optional[RetrievalRagStoreConfigRagRetrievalConfigFilter] = None
    """Optional. Config for filters."""

    hybrid_search: Optional[RetrievalRagStoreConfigRagRetrievalConfigHybridSearch] = None
    """Optional. Config for Hybrid Search."""

    ranking: Optional[RetrievalRagStoreConfigRagRetrievalConfigRanking] = None
    """Optional. Config for ranking and reranking."""

    top_k: Optional[int] = None
    """Optional. The number of contexts to retrieve."""


class RetrievalRagStoreConfig(BaseModel):
    """Used to specify configuration for RagStore."""

    rag_resources: Optional[List[RetrievalRagStoreConfigRagResource]] = None
    """Optional. The representation of the rag source."""

    rag_retrieval_config: Optional[RetrievalRagStoreConfigRagRetrievalConfig] = None
    """Optional. The retrieval config for the Rag query."""

    similarity_top_k: Optional[int] = None
    """Optional. Number of top k results to return from the selected corpora."""

    vector_distance_threshold: Optional[float] = None
    """Optional. Only return results with vector distance smaller than the threshold."""


class RetrievalVertexAISearchConfig(BaseModel):
    """Used to specify configuration for VertexAISearch."""

    datastores: Optional[List[str]] = None
    """Optional. Used to specify Vertex AI Search datastores."""

    engine: Optional[str] = None
    """Optional. Used to specify Vertex AI Search engine."""


class Retrieval(BaseModel):
    """A tool that can be used by the model to retrieve files."""

    type: Literal["retrieval"]

    exa_ai_search_config: Optional[RetrievalExaAISearchConfig] = None
    """Used to specify configuration for ExaAISearch."""

    parallel_ai_search_config: Optional[RetrievalParallelAISearchConfig] = None
    """Used to specify configuration for ParallelAISearch."""

    rag_store_config: Optional[RetrievalRagStoreConfig] = None
    """Used to specify configuration for RagStore."""

    retrieval_types: Optional[List[Literal["vertex_ai_search", "rag_store", "exa_ai_search", "parallel_ai_search"]]] = (
        None
    )
    """The types of file retrieval to enable."""

    vertex_ai_search_config: Optional[RetrievalVertexAISearchConfig] = None
    """Used to specify configuration for VertexAISearch."""


Tool: TypeAlias = Annotated[
    Union[Function, CodeExecution, URLContext, ComputerUse, MCPServer, GoogleSearch, FileSearch, GoogleMaps, Retrieval],
    PropertyInfo(discriminator="type"),
]
