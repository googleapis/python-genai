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
# pylint: disable=protected-access


"""Tests for the deferred import of the NextGen backends and interactions.

The client exposes the interactions/webhooks/agents/nextgen backends through
properties that import the heavy ``_gaos`` backend only on first access, and the
top-level package exposes ``interactions`` as a lazy module attribute. These
tests exercise those deferred-import paths: each accessor builds the correct
backend, memoizes it, and (for agents) emits the experimental warning.
"""

import sys

import pytest

from ... import Client
from ... import client as client_module
from ..._gaos.google_genai import AsyncGeminiNextGenAgents
from ..._gaos.google_genai import AsyncGeminiNextGenInteractions
from ..._gaos.google_genai import AsyncGeminiNextGenWebhooks
from ..._gaos.google_genai import GeminiNextGenAgents
from ..._gaos.google_genai import GeminiNextGenInteractions
from ..._gaos.google_genai import GeminiNextGenWebhooks
from ..._gaos.sdk import AsyncGenAI
from ..._gaos.sdk import GenAI

_GENAI_PACKAGE = Client.__module__.rsplit('.', 1)[0]


@pytest.fixture(autouse=True)
def _fresh_env(monkeypatch):
  monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
  for var in (
      'GOOGLE_CLOUD_PROJECT',
      'GEMINI_API_KEY',
      'GOOGLE_CLOUD_LOCATION',
  ):
    monkeypatch.delenv(var, raising=False)
  # ``agents`` warns once per process via a module global; reset it so every
  # test observes deterministic warning behavior regardless of test order.
  monkeypatch.setattr(client_module, '_agent_experimental_warned', False)


def test_sync_nextgen_client_is_lazy_and_cached():
  client = Client()
  nextgen = client._nextgen_client
  assert isinstance(nextgen, GenAI)
  assert client._nextgen_client is nextgen


def test_sync_interactions_is_lazy_and_cached():
  client = Client()
  interactions = client.interactions
  assert isinstance(interactions, GeminiNextGenInteractions)
  assert client.interactions is interactions


def test_sync_webhooks_is_lazy_and_cached():
  client = Client()
  webhooks = client.webhooks
  assert isinstance(webhooks, GeminiNextGenWebhooks)
  assert client.webhooks is webhooks


def test_sync_agents_is_lazy_cached_and_warns():
  client = Client()
  with pytest.warns(UserWarning, match='experimental'):
    agents = client.agents
  assert isinstance(agents, GeminiNextGenAgents)
  assert client.agents is agents


def test_async_nextgen_client_is_lazy_and_cached():
  client = Client()
  nextgen = client.aio._nextgen_client
  assert isinstance(nextgen, AsyncGenAI)
  assert client.aio._nextgen_client is nextgen


def test_async_interactions_is_lazy_and_cached():
  client = Client()
  interactions = client.aio.interactions
  assert isinstance(interactions, AsyncGeminiNextGenInteractions)
  assert client.aio.interactions is interactions


def test_async_webhooks_is_lazy_and_cached():
  client = Client()
  webhooks = client.aio.webhooks
  assert isinstance(webhooks, AsyncGeminiNextGenWebhooks)
  assert client.aio.webhooks is webhooks


def test_async_agents_is_lazy_cached_and_warns():
  client = Client()
  with pytest.warns(UserWarning, match='experimental'):
    agents = client.aio.agents
  assert isinstance(agents, AsyncGeminiNextGenAgents)
  assert client.aio.agents is agents


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason=(
        'Package-level lazy interactions attribute is a public-SDK-only'
        ' feature.'
    ),
)
def test_package_lazily_exposes_interactions_submodule():
  package = sys.modules[_GENAI_PACKAGE]
  # Drop any memoized attribute so the lazy ``__getattr__`` path runs.
  package.__dict__.pop('interactions', None)
  interactions = package.interactions
  assert interactions.__name__ == f'{_GENAI_PACKAGE}.interactions'
  assert interactions is sys.modules[f'{_GENAI_PACKAGE}.interactions']
