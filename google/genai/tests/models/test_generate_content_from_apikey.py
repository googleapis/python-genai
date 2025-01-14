import pytest
from .. import pytest_helper

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
)


def test_simple_request(client):
  # TODO(b/388917450): Add Vertex AI in Express mode test suite
  client._api_client.project = None
  client._api_client.location = None

  # To record a replay file, use an api key (from Vertex AI in Express mode).
  # API mode will not work if the API key is a ML Dev API key.
  client._api_client.api_key = 'vertex_api_key'
  if not client._api_client.vertexai:
    return
  response = client.models.generate_content(
      model='gemini-1.5-flash-002', contents='Tell me a joke.'
  )
  assert response.text