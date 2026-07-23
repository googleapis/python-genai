"""Model-agnostic pytest suite for FallbackPolicy."""

import asyncio
import copy
import os
import sys
from unittest.mock import AsyncMock, MagicMock
import pytest

root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import google  # noqa: E402

google.__path__.append(os.path.join(root_dir, "google"))
import google.genai  # noqa: E402

google.genai.__path__.append(os.path.join(root_dir, "google", "genai"))

from google.genai._fallback import APIError, FallbackPolicy  # noqa: E402


class CustomStatusException(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code


class ResponseStatusException(Exception):
    def __init__(self, status_code: int):
        self.response = MagicMock(status_code=status_code)


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


def test_max_retries_threshold_exceeded():
    """1. Max Retries Threshold: Re-raises underlying APIError when max_retries reached."""
    policy = FallbackPolicy(
        fallback_models=["model-b", "model-c", "model-d"], max_retries=3
    )
    error_429 = APIError(429, {"message": "Resource Exhausted"})
    mock_func = MagicMock(
        side_effect=[error_429, error_429, error_429, "should_not_reach"]
    )

    with pytest.raises(APIError) as exc_info:
        policy.execute_sync(mock_func, model="model-a")

    assert exc_info.value.code == 429
    assert mock_func.call_count == 3
    assert mock_func.call_args_list[0].kwargs["model"] == "model-a"
    assert mock_func.call_args_list[1].kwargs["model"] == "model-b"
    assert mock_func.call_args_list[2].kwargs["model"] == "model-c"


@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_non_retryable_http_errors_fail_fast(status_code):
    """2. Non-Retryable HTTP Errors: Fail fast on attempt 1 without attempting fallbacks."""
    policy = FallbackPolicy(fallback_models=["fallback-model"])
    error_non_retryable = APIError(
        status_code, {"message": "Permission or Client Error"}
    )
    mock_func = MagicMock(side_effect=error_non_retryable)

    with pytest.raises(APIError) as exc_info:
        policy.execute_sync(mock_func, model="primary-model")

    assert exc_info.value.code == status_code
    assert mock_func.call_count == 1
    assert mock_func.call_args.kwargs["model"] == "primary-model"


def test_combined_model_and_region_matrix():
    """3. Combined Model + Region Matrix: Evaluates combinations in order up to max_retries."""
    policy = FallbackPolicy(
        fallback_models=["model-b", "model-c"],
        fallback_locations=["europe-west9", "europe-west1"],
        max_retries=10,
    )
    error_503 = APIError(503, {"message": "Unavailable"})

    # 3 models x 3 locations = 9 combinations
    mock_func = MagicMock(side_effect=[error_503] * 8 + ["matrix_success"])

    result = policy.execute_sync(mock_func, model="model-a", location="us-central1")

    assert result == "matrix_success"
    assert mock_func.call_count == 9

    expected_calls = [
        ("model-a", "us-central1"),
        ("model-a", "europe-west9"),
        ("model-a", "europe-west1"),
        ("model-b", "us-central1"),
        ("model-b", "europe-west9"),
        ("model-b", "europe-west1"),
        ("model-c", "us-central1"),
        ("model-c", "europe-west9"),
        ("model-c", "europe-west1"),
    ]

    for idx, (expected_model, expected_location) in enumerate(expected_calls):
        call_kwargs = mock_func.call_args_list[idx].kwargs
        assert call_kwargs["model"] == expected_model
        assert call_kwargs["location"] == expected_location


@pytest.mark.asyncio
async def test_high_concurrency_async_stress():
    """4. High-Concurrency Async Stress Test: 100 concurrent async tasks execute safely."""
    policy = FallbackPolicy(fallback_models=["backup-model"])
    error_503 = APIError(503, {"message": "Service Unavailable"})

    async def mock_api(task_id: int, model: str):
        if model == "primary-model":
            raise error_503
        return f"task_{task_id}_success"

    tasks = [
        policy.execute_async(mock_api, task_id=i, model="primary-model")
        for i in range(100)
    ]

    results = await asyncio.gather(*tasks)
    assert len(results) == 100
    for i in range(100):
        assert results[i] == f"task_{i}_success"


def test_payload_mutability_audit():
    """5. Payload Mutability Audit: Complex nested kwargs remain unmutated across retries."""
    policy = FallbackPolicy(fallback_models=["model-b", "model-c"])
    error_429 = APIError(429, {"message": "Rate limit"})

    nested_contents = [{"role": "user", "parts": [{"text": "Generate analysis"}]}]
    nested_config = {
        "temperature": 0.7,
        "safety_settings": [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_LOW_AND_ABOVE",
            }
        ],
    }

    contents_copy = copy.deepcopy(nested_contents)
    config_copy = copy.deepcopy(nested_config)

    def side_effect(**kwargs):
        # Mutate the kwargs passed to the function to test isolation
        kwargs["contents"][0]["parts"][0]["text"] = "MUTATED"
        kwargs["config"]["temperature"] = 999.0
        if kwargs["model"] != "model-c":
            raise error_429
        return "success"

    mock_func = MagicMock(side_effect=side_effect)

    result = policy.execute_sync(
        mock_func,
        model="model-a",
        contents=nested_contents,
        config=nested_config,
    )

    assert result == "success"
    # Original user objects MUST NOT be mutated by retries or inner function calls
    assert nested_contents == contents_copy
    assert nested_config == config_copy


def test_status_code_extraction_support():
    """Extracts status code from status_code attribute or response.status_code."""
    policy = FallbackPolicy(fallback_models=["model-b"])

    mock_func1 = MagicMock(side_effect=[CustomStatusException(429), "success_custom"])
    result1 = policy.execute_sync(mock_func1, model="model-a")
    assert result1 == "success_custom"

    mock_func2 = MagicMock(side_effect=[ResponseStatusException(503), "success_resp"])
    result2 = policy.execute_sync(mock_func2, model="model-a")
    assert result2 == "success_resp"


def test_on_fallback_hook():
    """Triggers on_fallback hook with exception, attempt index, and next payload."""
    hook_calls = []

    def on_fallback(exc, attempt, next_payload):
        hook_calls.append((exc, attempt, next_payload["model"]))

    policy = FallbackPolicy(fallback_models=["model-b"], on_fallback=on_fallback)
    error_429 = APIError(429, {"message": "Limit"})
    mock_func = MagicMock(side_effect=[error_429, "hook_success"])

    result = policy.execute_sync(mock_func, model="model-a")

    assert result == "hook_success"
    assert len(hook_calls) == 1
    assert hook_calls[0][0] == error_429
    assert hook_calls[0][1] == 1
    assert hook_calls[0][2] == "model-b"
