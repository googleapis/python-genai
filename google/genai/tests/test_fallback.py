"""Model-agnostic pytest suite for FallbackPolicy."""

import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import google
google.__path__.append(os.path.join(root_dir, "google"))
import google.genai
google.genai.__path__.append(os.path.join(root_dir, "google", "genai"))

from google.genai._fallback import FallbackPolicy, APIError

def test_sync_primary_success():
    policy = FallbackPolicy(fallback_models=["fallback-model-b"])
    mock_func = MagicMock(return_value="primary_success")

    result = policy.execute_sync(mock_func, model="primary-model-a", contents="Hello")
    
    assert result == "primary_success"
    assert mock_func.call_count == 1
    assert mock_func.call_args.kwargs["model"] == "primary-model-a"

def test_sync_model_fallback_on_429():
    policy = FallbackPolicy(fallback_models=["fallback-model-b"])
    error_429 = APIError(429, {"message": "Rate limit exceeded"})
    mock_func = MagicMock(side_effect=[error_429, "fallback_success"])

    result = policy.execute_sync(mock_func, model="primary-model-a", contents="Hello")

    assert result == "fallback_success"
    assert mock_func.call_count == 2
    assert mock_func.call_args_list[0].kwargs["model"] == "primary-model-a"
    assert mock_func.call_args_list[1].kwargs["model"] == "fallback-model-b"

def test_sync_region_fallback():
    policy = FallbackPolicy(fallback_locations=["europe-west9", "europe-west1"])
    error_503 = APIError(503, {"message": "Region unavailable"})
    mock_func = MagicMock(side_effect=[error_503, "region_fallback_success"])

    result = policy.execute_sync(
        mock_func, model="user-configured-model", location="us-central1"
    )

    assert result == "region_fallback_success"
    assert mock_func.call_count == 2
    assert mock_func.call_args_list[0].kwargs["location"] == "us-central1"
    assert mock_func.call_args_list[1].kwargs["location"] == "europe-west9"

@pytest.mark.asyncio
async def test_async_fallback_execution():
    policy = FallbackPolicy(fallback_models=["backup-async-model"])
    error_504 = APIError(504, {"message": "Gateway Timeout"})
    mock_async = AsyncMock(side_effect=[error_504, "async_success"])

    result = await policy.execute_async(mock_async, model="primary-async-model")
    assert result == "async_success"
    assert mock_async.call_count == 2
    assert mock_async.call_args_list[1].kwargs["model"] == "backup-async-model"
