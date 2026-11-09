"""Fixtures for the api-mode live tests.

These tests deliberately do not go through pytest_helper.setup(): the live
module is a bidirectional WebSocket session, which cannot be expressed as the
request/response table the shared corpus is built on, and which the replay
client cannot record. setup() would also emit a _test_table.json that the other
five SDKs' harnesses would try to execute.

The `client` fixture in the parent conftest still applies, and in --mode=api it
yields a client that talks to the real backend.
"""

import pytest


@pytest.fixture
def http_options():
  """Required by the parent `client` fixture.

  Normally injected by pytest_helper.setup(); live tests use the SDK defaults.
  """
  return None


@pytest.fixture
def location_override():
  """Pins the Vertex client to a region for the live model.

  gemini-live-2.5-flash-native-audio is not served on the global endpoint: a
  setup there is rejected with 1008 "Publisher model ... was not found". It is
  available in us-central1, us-east5 and europe-west4. The Agent Platform
  wrapper sets GOOGLE_CLOUD_LOCATION=global for the shared suite, so the live
  tests override it here rather than changing the wrapper.
  """
  return 'us-central1'
