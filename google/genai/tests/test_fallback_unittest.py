"""Model-agnostic unittest suite for FallbackPolicy."""

import asyncio
import copy
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

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


class TestModelAgnosticFallbackPolicy(unittest.TestCase):
    def test_sync_primary_success(self):
        """Primary model succeeds without triggering fallbacks."""
        policy = FallbackPolicy(fallback_models=["fallback-model-b"])
        mock_func = MagicMock(return_value="primary_success")

        result = policy.execute_sync(
            mock_func, model="primary-model-a", contents="Hello"
        )

        self.assertEqual(result, "primary_success")
        self.assertEqual(mock_func.call_count, 1)
        self.assertEqual(mock_func.call_args.kwargs["model"], "primary-model-a")

    def test_sync_model_fallback_on_429(self):
        """Failover occurs to user-specified fallback model on 429 Rate Limit."""
        policy = FallbackPolicy(fallback_models=["fallback-model-b"])
        error_429 = APIError(429, {"message": "Rate limit exceeded"})
        mock_func = MagicMock(side_effect=[error_429, "fallback_success"])

        result = policy.execute_sync(
            mock_func, model="primary-model-a", contents="Hello"
        )

        self.assertEqual(result, "fallback_success")
        self.assertEqual(mock_func.call_count, 2)
        self.assertEqual(mock_func.call_args_list[0].kwargs["model"], "primary-model-a")
        self.assertEqual(
            mock_func.call_args_list[1].kwargs["model"], "fallback-model-b"
        )

    def test_sync_region_fallback(self):
        """Failover occurs across regions when location fallback is configured."""
        policy = FallbackPolicy(fallback_locations=["europe-west9", "europe-west1"])
        error_503 = APIError(503, {"message": "Region unavailable"})
        mock_func = MagicMock(side_effect=[error_503, "region_fallback_success"])

        result = policy.execute_sync(
            mock_func, model="user-configured-model", location="us-central1"
        )

        self.assertEqual(result, "region_fallback_success")
        self.assertEqual(mock_func.call_count, 2)
        self.assertEqual(mock_func.call_args_list[0].kwargs["location"], "us-central1")
        self.assertEqual(mock_func.call_args_list[1].kwargs["location"], "europe-west9")

    def test_custom_is_retryable_predicate(self):
        """Custom is_retryable predicate function determines fallback eligibility."""
        custom_policy = FallbackPolicy(
            fallback_models=["backup-model"],
            is_retryable=lambda exc: getattr(exc, "code", None) == 500,
        )
        error_500 = APIError(500, {"message": "Internal Error"})
        mock_func = MagicMock(side_effect=[error_500, "custom_predicate_success"])

        result = custom_policy.execute_sync(mock_func, model="primary-model")
        self.assertEqual(result, "custom_predicate_success")
        self.assertEqual(mock_func.call_count, 2)

    def test_async_fallback_execution(self):
        """Async API calls correctly execute fallbacks."""

        async def run_test():
            policy = FallbackPolicy(fallback_models=["backup-async-model"])
            error_504 = APIError(504, {"message": "Gateway Timeout"})
            mock_async = AsyncMock(side_effect=[error_504, "async_success"])

            result = await policy.execute_async(mock_async, model="primary-async-model")
            self.assertEqual(result, "async_success")
            self.assertEqual(mock_async.call_count, 2)
            self.assertEqual(
                mock_async.call_args_list[1].kwargs["model"],
                "backup-async-model",
            )

        asyncio.run(run_test())

    def test_max_retries_threshold_exceeded(self):
        """1. Max Retries Threshold: Re-raises underlying APIError when max_retries reached."""
        policy = FallbackPolicy(
            fallback_models=["model-b", "model-c", "model-d"], max_retries=3
        )
        error_429 = APIError(429, {"message": "Resource Exhausted"})
        mock_func = MagicMock(
            side_effect=[error_429, error_429, error_429, "should_not_reach"]
        )

        with self.assertRaises(APIError) as cm:
            policy.execute_sync(mock_func, model="model-a")

        self.assertEqual(cm.exception.code, 429)
        self.assertEqual(mock_func.call_count, 3)
        self.assertEqual(mock_func.call_args_list[0].kwargs["model"], "model-a")
        self.assertEqual(mock_func.call_args_list[1].kwargs["model"], "model-b")
        self.assertEqual(mock_func.call_args_list[2].kwargs["model"], "model-c")

    def test_non_retryable_http_errors_fail_fast(self):
        """2. Non-Retryable HTTP Errors: Fail fast on attempt 1 for 400, 401, 403."""
        policy = FallbackPolicy(fallback_models=["fallback-model"])

        for status_code in [400, 401, 403]:
            error_non_retryable = APIError(
                status_code, {"message": f"Error {status_code}"}
            )
            mock_func = MagicMock(side_effect=error_non_retryable)

            with self.assertRaises(APIError) as cm:
                policy.execute_sync(mock_func, model="primary-model")

            self.assertEqual(cm.exception.code, status_code)
            self.assertEqual(mock_func.call_count, 1)
            self.assertEqual(mock_func.call_args.kwargs["model"], "primary-model")

    def test_combined_model_and_region_matrix(self):
        """3. Combined Model + Region Matrix: Evaluates matrix combinations in order up to max_retries."""
        policy = FallbackPolicy(
            fallback_models=["model-b", "model-c"],
            fallback_locations=["europe-west9", "europe-west1"],
            max_retries=10,
        )
        error_503 = APIError(503, {"message": "Unavailable"})

        mock_func = MagicMock(side_effect=[error_503] * 8 + ["matrix_success"])

        result = policy.execute_sync(mock_func, model="model-a", location="us-central1")

        self.assertEqual(result, "matrix_success")
        self.assertEqual(mock_func.call_count, 9)

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
            self.assertEqual(call_kwargs["model"], expected_model)
            self.assertEqual(call_kwargs["location"], expected_location)

    def test_high_concurrency_async_stress(self):
        """4. High-Concurrency Async Stress Test: 100 concurrent async tasks execute safely."""

        async def run_stress_test():
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
            self.assertEqual(len(results), 100)
            for i in range(100):
                self.assertEqual(results[i], f"task_{i}_success")

        asyncio.run(run_stress_test())

    def test_payload_mutability_audit(self):
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

        self.assertEqual(result, "success")
        self.assertEqual(nested_contents, contents_copy)
        self.assertEqual(nested_config, config_copy)

    def test_status_code_extraction_support(self):
        """Extracts status code from status_code attribute or response.status_code."""
        policy = FallbackPolicy(fallback_models=["model-b"])

        mock_func1 = MagicMock(
            side_effect=[CustomStatusException(429), "success_custom"]
        )
        result1 = policy.execute_sync(mock_func1, model="model-a")
        self.assertEqual(result1, "success_custom")

        mock_func2 = MagicMock(
            side_effect=[ResponseStatusException(503), "success_resp"]
        )
        result2 = policy.execute_sync(mock_func2, model="model-a")
        self.assertEqual(result2, "success_resp")

    def test_on_fallback_hook(self):
        """Triggers on_fallback hook with exception, attempt index, and next payload."""
        hook_calls = []

        def on_fallback(exc, attempt, next_payload):
            hook_calls.append((exc, attempt, next_payload["model"]))

        policy = FallbackPolicy(fallback_models=["model-b"], on_fallback=on_fallback)
        error_429 = APIError(429, {"message": "Limit"})
        mock_func = MagicMock(side_effect=[error_429, "hook_success"])

        result = policy.execute_sync(mock_func, model="model-a")

        self.assertEqual(result, "hook_success")
        self.assertEqual(len(hook_calls), 1)
        self.assertEqual(hook_calls[0][0], error_429)
        self.assertEqual(hook_calls[0][1], 1)
        self.assertEqual(hook_calls[0][2], "model-b")


if __name__ == "__main__":
    unittest.main()
