import sys
import os

# Set up path so we can import and run scripts as if they were in the workspace.
sys.path.append(os.getcwd())

from third_party.py.google.genai import types
from third_party.py.google.genai import models
from third_party.py.google.genai import _common
import json

class MockApiClient:
    def __init__(self):
        self.vertexai = True
        self.location = 'us-central1'
        self.project = 'test-project'

def test_transformation():
    tool = types.Tool(
        retrieval=types.Retrieval(
            vertex_rag_store=types.VertexRagStore(
                rag_resources=[
                    types.VertexRagStoreRagResource(
                        rag_corpus='projects/test-project/locations/us-central1/ragCorpora/test-corpus'
                    )
                ],
                rag_retrieval_config=types.RagRetrievalConfig(
                    filter=types.RagRetrievalConfigFilter(
                        metadata_filter='color = "red"',
                    ),
                ),
            )
        ),
    )

    api_client = MockApiClient()
    # Mocking internal transform
    transformed = models._Tool_to_vertex(api_client, tool)
    final_dict = _common.convert_to_dict(transformed)
    print(json.dumps(final_dict, indent=2))

if __name__ == '__main__':
    test_transformation()
