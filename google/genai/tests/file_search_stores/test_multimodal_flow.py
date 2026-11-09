# Copyright 2026 Google LLC
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

import io
import os
import time
import pydantic
from ... import types
from .. import pytest_helper


class MultimodalFlowParams(pydantic.BaseModel):
  display_name: str
  query: str
  text_content: str
  image_relative_path: str


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_multimodal_search_flow',
        parameters=MultimodalFlowParams(
            display_name='test-multimodal-store',
            query=(
                'Find the photo of the dog in the park, what is the dog doing?'
            ),
            text_content='This is a test text file content for file search.',
            image_relative_path='../data/dog.jpg',
        ),
        exception_if_vertex='supported',
    )
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='multimodal_search_flow',
    test_table=test_table,
    http_options={
        'api_version': 'v1beta',
        'base_url': (
            'https://autopush-generativelanguage.sandbox.googleapis.com'
        ),
    },
)


def multimodal_search_flow(client, parameters: MultimodalFlowParams):
  # 1. Create Store
  store = None
  try:
    store = client.file_search_stores.create(
        config=types.CreateFileSearchStoreConfig(
            display_name=parameters.display_name,
            embedding_model='models/gemini-embedding-2-preview',
        )
    )

    # 2. Upload Text
    text_file = io.BytesIO(parameters.text_content.encode('utf-8'))
    op_text = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store.name,
        file=text_file,
        config=types.UploadToFileSearchStoreConfig(mime_type='text/plain'),
    )

    original_cwd = os.getcwd()
    try:
      # cd is necessary because the recorder records the file path, so we need to use a relative path here.
      os.chdir(os.path.dirname(__file__))
      op_image = client.file_search_stores.upload_to_file_search_store(
          file_search_store_name=store.name,
          file=parameters.image_relative_path,
          config=types.UploadToFileSearchStoreConfig(mime_type='image/png'),
      )
    finally:
      os.chdir(original_cwd)

    # 4. Wait for operations
    # In replay mode, these might be fast or pre-recorded.
    # In live mode, we need to poll.
    while not op_text.done:
      time.sleep(1)
      op_text = client.operations.get(op_text)

    if op_image:
      while not op_image.done:
        time.sleep(1)
        op_image = client.operations.get(op_image)

    # 5. Search
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=parameters.query,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store.name]
                    )
                )
            ]
        ),
    )

    # Verify response has grounding metadata
    assert response.candidates[0].grounding_metadata is not None

    # 6. Download Media
    # Extract Media ID from grounding chunks if available
    blob_media_id = None
    if response.candidates[0].grounding_metadata.grounding_chunks:
      for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
        if chunk.retrieved_context and chunk.retrieved_context.media_id:
          blob_media_id = chunk.retrieved_context.media_id
          break

    # If we are on MLDev, we expect a Media ID and should be able to download it.
    if not client.vertexai:
      if not blob_media_id:
        raise ValueError('No media_id found in grounding metadata to test download.')
      content = client.file_search_stores.download_media(
          media_id=blob_media_id
      )
      assert content is not None
    else:
      # On Vertex, we expect download_media to fail if we call it.
      with pytest_helper.exception_if_vertex(client, ValueError):
        if blob_media_id:
          client.file_search_stores.download_media(media_id=blob_media_id)
  finally:
    if store:
      client.file_search_stores.delete(
          name=store.name, config=types.DeleteFileSearchStoreConfig(force=True)
      )
