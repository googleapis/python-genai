from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from prometheus_client import Counter, Histogram
from ..core.transcript_processor import TranscriptProcessor, TranscriptChunk
from ..core.question_optimizer import QuestionOptimizer, QuestionDependency
from ..api.gemini_client import GeminiClient, GeminiResponse
from ..cache.hybrid_cache import HybridCache
from ..config.settings import settings

# Prometheus metrics
PROCESSING_TIME = Histogram(
    'transcript_processing_seconds',
    'Time spent processing transcripts'
)
QUESTION_PROCESSING_TIME = Histogram(
    'question_processing_seconds',
    'Time spent processing questions'
)
TOTAL_QUESTIONS = Counter(
    'total_questions_processed',
    'Total number of questions processed'
)

@dataclass
class AnalysisResult:
    """Container for analysis results."""
    video_id: str
    questions: List[str]
    answers: List[str]
    processing_time: float
    cache_hit_ratio: float

class TranscriptAnalyzer:
    """Main orchestrator for transcript analysis system."""
    
    def __init__(self):
        self.transcript_processor = TranscriptProcessor()
        self.question_optimizer = QuestionOptimizer()
        self.gemini_client = GeminiClient()
        self.cache = HybridCache()
    
    async def analyze_transcript(
        self,
        video_id: str,
        transcript: str,
        questions: List[str]
    ) -> AnalysisResult:
        """Main entry point for transcript analysis."""
        with PROCESSING_TIME.time():
            # Process transcript into chunks
            chunks = self.transcript_processor.chunk_transcript(transcript)
            
            # Analyze and optimize questions
            with QUESTION_PROCESSING_TIME.time():
                dependencies = self.question_optimizer.analyze_dependencies(questions)
                question_batches = self.question_optimizer.optimize_order(dependencies)
            
            # Process each batch of questions
            all_answers = []
            cache_hits = 0
            total_questions = 0
            
            for batch_indices in question_batches:
                batch_questions = [questions[i] for i in batch_indices]
                batch_answers = await self._process_question_batch(
                    video_id,
                    chunks,
                    batch_questions
                )
                all_answers.extend(batch_answers)
                total_questions += len(batch_questions)
                TOTAL_QUESTIONS.inc(len(batch_questions))
            
            # Calculate cache hit ratio
            cache_hit_ratio = cache_hits / total_questions if total_questions > 0 else 0
            
            return AnalysisResult(
                video_id=video_id,
                questions=questions,
                answers=all_answers,
                processing_time=PROCESSING_TIME._sum.get(),
                cache_hit_ratio=cache_hit_ratio
            )
    
    async def _process_question_batch(
        self,
        video_id: str,
        chunks: List[TranscriptChunk],
        questions: List[str]
    ) -> List[str]:
        """Process a batch of questions with caching."""
        answers = []
        
        for question in questions:
            # Try to get context from cache
            cached_contexts = self.cache.get_context(question, video_id)
            
            if cached_contexts:
                # Use cached contexts
                context = "\n".join(cached_contexts)
            else:
                # Find relevant chunks for the question
                relevant_chunks = self._find_relevant_chunks(question, chunks)
                context = "\n".join(chunk.text for chunk in relevant_chunks)
                
                # Cache the contexts
                self.cache.store_context(
                    question,
                    video_id,
                    [chunk.text for chunk in relevant_chunks]
                )
            
            # Generate answer using Gemini
            response = await self.gemini_client.generate_answers(
                context=context,
                questions=[question]
            )
            
            if response and self.gemini_client.validate_response(response[0]):
                answers.append(response[0].text)
            else:
                answers.append("Unable to generate a valid answer.")
        
        return answers
    
    def _find_relevant_chunks(
        self,
        question: str,
        chunks: List[TranscriptChunk]
    ) -> List[TranscriptChunk]:
        """Find the most relevant chunks for a question."""
        if not chunks:
            return []
        
        # Use semantic similarity to find relevant chunks
        relevant_chunks = []
        for chunk in chunks:
            similarity = self.transcript_processor.get_semantic_similarity(
                question,
                chunk.text
            )
            if similarity > 0.5:  # Threshold for relevance
                relevant_chunks.append(chunk)
        
        # Sort by similarity and take top 3
        relevant_chunks.sort(
            key=lambda x: self.transcript_processor.get_semantic_similarity(
                question,
                x.text
            ),
            reverse=True
        )
        
        return relevant_chunks[:3]
    
    def clear_cache(self, video_id: Optional[str] = None) -> None:
        """Clear the cache for a specific video or all videos."""
        self.cache.clear_cache(video_id) 