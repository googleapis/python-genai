from typing import List, Optional, Dict, Any
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from pydantic import BaseModel, Field
from ..config.settings import settings
import time
from prometheus_client import Counter, Histogram

# Prometheus metrics
API_CALLS = Counter('gemini_api_calls_total', 'Total number of API calls made')
API_ERRORS = Counter('gemini_api_errors_total', 'Total number of API errors')
API_LATENCY = Histogram('gemini_api_latency_seconds', 'API call latency in seconds')

class GeminiResponse(BaseModel):
    """Validated response from Gemini API."""
    text: str
    safety_ratings: List[Dict[str, Any]] = Field(default_factory=list)
    prompt_feedback: Optional[Dict[str, Any]] = None

class GeminiClient:
    """Client for interacting with the Gemini API with retry logic and rate limiting."""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self._last_request_time = 0
        self._request_count = 0
        self._window_start = time.time()
    
    def _check_rate_limit(self) -> None:
        """Implement rate limiting logic."""
        current_time = time.time()
        
        # Reset window if needed
        if current_time - self._window_start >= settings.RATE_LIMIT_PERIOD:
            self._request_count = 0
            self._window_start = current_time
        
        # Check if we're over the limit
        if self._request_count >= settings.RATE_LIMIT_REQUESTS:
            sleep_time = settings.RATE_LIMIT_PERIOD - (current_time - self._window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._request_count = 0
            self._window_start = time.time()
        
        # Ensure minimum delay between requests
        time_since_last = current_time - self._last_request_time
        if time_since_last < 0.1:  # 100ms minimum delay
            time.sleep(0.1 - time_since_last)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_random_exponential(multiplier=settings.RETRY_DELAY, max=60),
        retry=retry_if_exception_type((Exception)),
        before_sleep=lambda retry_state: API_ERRORS.inc()
    )
    async def generate_answers(
        self,
        context: str,
        questions: List[str],
        temperature: float = 0.7
    ) -> List[GeminiResponse]:
        """Generate answers for a batch of questions with retry logic."""
        self._check_rate_limit()
        
        with API_LATENCY.time():
            API_CALLS.inc()
            try:
                # Prepare the prompt
                prompt = self._prepare_prompt(context, questions)
                
                # Generate response
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": settings.MAX_TOKENS_PER_REQUEST
                    }
                )
                
                # Validate and parse response
                return self._parse_response(response)
            
            except Exception as e:
                API_ERRORS.inc()
                raise
    
    def _prepare_prompt(self, context: str, questions: List[str]) -> str:
        """Prepare the prompt with context and questions."""
        prompt = f"""Context:
{context}

Please answer the following questions based on the context above. Provide clear, concise answers:

"""
        for i, question in enumerate(questions, 1):
            prompt += f"{i}. {question}\n"
        
        return prompt
    
    def _parse_response(self, response: Any) -> List[GeminiResponse]:
        """Parse and validate the API response."""
        if not response.text:
            raise ValueError("Empty response from API")
        
        # Split response into individual answers
        answers = response.text.split('\n\n')
        validated_answers = []
        
        for answer in answers:
            if not answer.strip():
                continue
            
            validated_answers.append(GeminiResponse(
                text=answer.strip(),
                safety_ratings=response.safety_ratings if hasattr(response, 'safety_ratings') else [],
                prompt_feedback=response.prompt_feedback if hasattr(response, 'prompt_feedback') else None
            ))
        
        return validated_answers
    
    def validate_response(self, response: GeminiResponse) -> bool:
        """Validate response content for safety and quality."""
        # Check for minimum length
        if len(response.text.strip()) < 10:
            return False
        
        # Check safety ratings if available
        if response.safety_ratings:
            for rating in response.safety_ratings:
                if rating.get('probability', 0) > 0.8:  # High probability of unsafe content
                    return False
        
        return True 