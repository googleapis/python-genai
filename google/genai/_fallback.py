"""Model-agnostic fallback policy and middleware for Google GenAI SDK."""

import asyncio
import copy
import logging
import time
from typing import Any, Callable, List, Optional, TypeVar

try:
    from google.genai.errors import APIError
except ImportError:

    class APIError(Exception):  # type: ignore
        def __init__(self, code: int, response_json: Any = None):
            self.code = code
            self.response_json = response_json or {}
            super().__init__(f"APIError {code}: {response_json}")


logger = logging.getLogger("google.genai.fallback")

T = TypeVar("T")


def _extract_status_code(exc: Exception) -> Optional[int]:
    """Extracts HTTP status code across APIError, httpx, and requests exceptions."""
    if hasattr(exc, "code") and isinstance(getattr(exc, "code"), int):
        return getattr(exc, "code")
    if hasattr(exc, "status_code") and isinstance(getattr(exc, "status_code"), int):
        return getattr(exc, "status_code")
    response = getattr(exc, "response", None)
    if response is not None and hasattr(response, "status_code"):
        code = getattr(response, "status_code")
        if isinstance(code, int):
            return code
    return None


def _default_is_retryable(exc: Exception, status_codes: List[int]) -> bool:
    """Default predicate checking if an exception qualifies for fallback."""
    code = _extract_status_code(exc)
    if code is not None:
        return code in status_codes
    return False


class FallbackPolicy:
    """Production-grade, model-agnostic fallback middleware.

    This policy does not hardcode any model names. It accepts user-configured
    fallback models and/or locations dynamically at runtime.

    Attributes:
        fallback_models: Sequence of model names to try if the primary model fails.
        fallback_locations: Sequence of Vertex AI locations (regions) to try if primary fails.
        retry_status_codes: List of HTTP status codes that trigger a fallback (default: 429, 503, 504).
        is_retryable: Custom predicate function (exc -> bool) determining if an exception triggers fallback.
        max_retries: Hard upper bound on total attempts.
        backoff_factor: Optional exponential backoff multiplier in seconds (default: 0.0).
        on_fallback: Optional callback function called when a fallback attempt is initiated.
    """

    def __init__(
        self,
        fallback_models: Optional[List[str]] = None,
        fallback_locations: Optional[List[str]] = None,
        retry_status_codes: Optional[List[int]] = None,
        is_retryable: Optional[Callable[[Exception], bool]] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.0,
        on_fallback: Optional[Callable[[Exception, int, dict], None]] = None,
    ):
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        self.fallback_models = fallback_models or []
        self.fallback_locations = fallback_locations or []
        self.retry_status_codes = retry_status_codes or [429, 503, 504]
        self.is_retryable_custom = is_retryable
        self.max_retries = max_retries
        self.backoff_factor = max(0.0, backoff_factor)
        self.on_fallback = on_fallback

    def is_eligible_for_fallback(self, exc: Exception) -> bool:
        """Determines if the encountered error should trigger a fallback attempt."""
        if self.is_retryable_custom is not None:
            return self.is_retryable_custom(exc)
        return _default_is_retryable(exc, self.retry_status_codes)

    def _build_attempts_plan(self, kwargs: dict) -> List[dict]:
        """Builds a sequence of kwarg dictionary payloads to attempt sequentially."""
        primary_model = kwargs.get("model")
        primary_location = kwargs.get("location")

        # Build list of model targets
        model_targets = [primary_model] if primary_model else []
        for m in self.fallback_models:
            if m not in model_targets:
                model_targets.append(m)

        # Build list of location targets
        location_targets = [primary_location] if primary_location else []
        for loc in self.fallback_locations:
            if loc not in location_targets:
                location_targets.append(loc)

        plan = []

        # If model fallback sequence specified
        if self.fallback_models and not self.fallback_locations:
            for m in model_targets:
                payload = copy.deepcopy(kwargs)
                if m:
                    payload["model"] = m
                plan.append(payload)

        # If location fallback sequence specified
        elif self.fallback_locations and not self.fallback_models:
            for loc in location_targets:
                payload = copy.deepcopy(kwargs)
                if loc:
                    payload["location"] = loc
                plan.append(payload)

        # If both model and location fallbacks specified
        elif self.fallback_models and self.fallback_locations:
            for m in model_targets:
                for loc in location_targets:
                    payload = copy.deepcopy(kwargs)
                    if m:
                        payload["model"] = m
                    if loc:
                        payload["location"] = loc
                    plan.append(payload)
        else:
            # Default: execute with original kwargs
            plan.append(copy.deepcopy(kwargs))

        return plan[: self.max_retries]

    def _notify_and_delay_sync(
        self, exc: Exception, attempt_idx: int, total_attempts: int, next_payload: dict
    ) -> None:
        logger.warning(
            f"[GenAI Fallback] Attempt {attempt_idx}/{total_attempts} failed "
            f"with {type(exc).__name__}: {exc}. Retrying with next fallback configuration..."
        )
        if self.on_fallback is not None:
            try:
                self.on_fallback(exc, attempt_idx, next_payload)
            except Exception as hook_exc:
                logger.error(f"[GenAI Fallback] Error in on_fallback hook: {hook_exc}")

        if self.backoff_factor > 0:
            delay = self.backoff_factor * (2 ** (attempt_idx - 1))
            time.sleep(delay)

    async def _notify_and_delay_async(
        self, exc: Exception, attempt_idx: int, total_attempts: int, next_payload: dict
    ) -> None:
        logger.warning(
            f"[GenAI Fallback Async] Attempt {attempt_idx}/{total_attempts} failed "
            f"with {type(exc).__name__}: {exc}. Retrying with next fallback configuration..."
        )
        if self.on_fallback is not None:
            try:
                self.on_fallback(exc, attempt_idx, next_payload)
            except Exception as hook_exc:
                logger.error(
                    f"[GenAI Fallback Async] Error in on_fallback hook: {hook_exc}"
                )

        if self.backoff_factor > 0:
            delay = self.backoff_factor * (2 ** (attempt_idx - 1))
            await asyncio.sleep(delay)

    def execute_sync(self, func: Callable[..., T], **kwargs: Any) -> T:
        """Executes a synchronous API call through the fallback sequence."""
        attempts_plan = self._build_attempts_plan(kwargs)
        last_exception: Optional[Exception] = None

        for attempt_idx, payload in enumerate(attempts_plan, start=1):
            try:
                return func(**payload)
            except Exception as e:
                last_exception = e
                if self.is_eligible_for_fallback(e) and attempt_idx < len(
                    attempts_plan
                ):
                    next_payload = attempts_plan[attempt_idx]
                    self._notify_and_delay_sync(
                        e, attempt_idx, len(attempts_plan), next_payload
                    )
                    continue
                raise e

        if last_exception:
            raise last_exception
        raise RuntimeError("Fallback policy failed without raising an exception.")

    async def execute_async(self, func: Callable[..., Any], **kwargs: Any) -> Any:
        """Executes an asynchronous API call through the fallback sequence."""
        attempts_plan = self._build_attempts_plan(kwargs)
        last_exception: Optional[Exception] = None

        for attempt_idx, payload in enumerate(attempts_plan, start=1):
            try:
                return await func(**payload)
            except Exception as e:
                last_exception = e
                if self.is_eligible_for_fallback(e) and attempt_idx < len(
                    attempts_plan
                ):
                    next_payload = attempts_plan[attempt_idx]
                    await self._notify_and_delay_async(
                        e, attempt_idx, len(attempts_plan), next_payload
                    )
                    continue
                raise e

        if last_exception:
            raise last_exception
        raise RuntimeError("Fallback policy failed without raising an exception.")
