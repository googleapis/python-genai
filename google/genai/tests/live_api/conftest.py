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
