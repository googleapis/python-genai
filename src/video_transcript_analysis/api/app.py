from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from prometheus_client import make_asgi_app
from ..core.orchestrator import TranscriptAnalyzer, AnalysisResult
from ..config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Video Transcript Analysis API",
    description="API for analyzing video transcripts using Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Initialize analyzer
analyzer = TranscriptAnalyzer()

class TranscriptRequest(BaseModel):
    """Request model for transcript analysis."""
    video_id: str = Field(..., description="Unique identifier for the video")
    transcript: str = Field(..., description="The video transcript text")
    questions: List[str] = Field(..., description="List of questions to answer")

class AnalysisResponse(BaseModel):
    """Response model for transcript analysis."""
    video_id: str
    questions: List[str]
    answers: List[str]
    processing_time: float
    cache_hit_ratio: float

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze video transcript",
    description="Process a video transcript and answer a set of questions using AI"
)
async def analyze_transcript(request: TranscriptRequest) -> AnalysisResponse:
    """Analyze a video transcript and answer questions."""
    try:
        result = await analyzer.analyze_transcript(
            video_id=request.video_id,
            transcript=request.transcript,
            questions=request.questions
        )
        return AnalysisResponse(
            video_id=result.video_id,
            questions=result.questions,
            answers=result.answers,
            processing_time=result.processing_time,
            cache_hit_ratio=result.cache_hit_ratio
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transcript: {str(e)}"
        )

@app.delete(
    "/cache/{video_id}",
    summary="Clear cache",
    description="Clear the cache for a specific video or all videos"
)
async def clear_cache(video_id: Optional[str] = None):
    """Clear the cache for a specific video or all videos."""
    try:
        analyzer.clear_cache(video_id)
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )

@app.get(
    "/health",
    summary="Health check",
    description="Check if the API is healthy"
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 