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

  # To record a replay file, replace with api key (from Vertex AI Express).
  # API mode will not work if the API key is a ML Dev API key.
  # After recording, change the string back to 'key'.
  client._api_client._http_options.headers['x-goog-api-key'] = 'key'
  if not client._api_client.vertexai:
    return
  response = client.models.generate_content(
      model='gemini-2.0-flash-001', contents='Tell me a joke.'
  )
  assert response.text


def test_simple_request_stream(client):
  # TODO(b/388917450): Add Vertex AI in Express mode test suite
  client._api_client.project = None
  client._api_client.location = None

  # To record a replay file, replace with api key (from Vertex AI Express).
  # API mode will not work if the API key is a ML Dev API key.
  # After recording, change the string back to 'key'.
  client._api_client._http_options.headers['x-goog-api-key'] = 'key'
  if not client._api_client.vertexai:
    return

  response = client.models.generate_content_stream(
      model='gemini-2.0-flash-001', contents='Tell me a joke.'
  )

  assert any(chunk.text for chunk in response)
