from typing import List, Optional, Dict, Any
from cachetools import TTLCache
import redis
from sentence_transformers import SentenceTransformer
import numpy as np
from prometheus_client import Counter, Gauge
from ..config.settings import settings

# Prometheus metrics
CACHE_HITS = Counter('cache_hits_total', 'Total number of cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Total number of cache misses')
CACHE_SIZE = Gauge('cache_size_bytes', 'Current size of the cache in bytes')

class HybridCache:
    """Multi-layer caching system with semantic search capabilities."""
    
    def __init__(self):
        # Initialize in-memory cache
        self.memory_cache = TTLCache(
            maxsize=settings.CACHE_MAX_SIZE,
            ttl=settings.CACHE_TTL
        )
        
        # Initialize Redis if configured
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
            except redis.ConnectionError as e:
                print(f"Warning: Redis connection failed: {e}")
        
        # Initialize semantic search
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Failed to load semantic model: {e}")
            self.semantic_model = None
    
    def get_context(self, question: str, video_id: str) -> Optional[List[str]]:
        """Get context from cache using multi-layer lookup."""
        # Try in-memory cache first
        cache_key = f"{video_id}:{question}"
        if cache_key in self.memory_cache:
            CACHE_HITS.inc()
            return self.memory_cache[cache_key]
        
        # Try Redis if available
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    CACHE_HITS.inc()
                    result = eval(cached_data)  # Safe as we control the input
                    self.memory_cache[cache_key] = result
                    return result
            except redis.RedisError:
                pass
        
        # Try semantic search as fallback
        if self.semantic_model:
            try:
                similar_contexts = self._semantic_search(question, video_id)
                if similar_contexts:
                    CACHE_HITS.inc()
                    self.memory_cache[cache_key] = similar_contexts
                    if self.redis_client:
                        self.redis_client.setex(
                            cache_key,
                            settings.CACHE_TTL,
                            str(similar_contexts)
                        )
                    return similar_contexts
            except Exception as e:
                print(f"Warning: Semantic search failed: {e}")
        
        CACHE_MISSES.inc()
        return None
    
    def store_context(
        self,
        question: str,
        video_id: str,
        contexts: List[str]
    ) -> None:
        """Store context in all cache layers."""
        cache_key = f"{video_id}:{question}"
        
        # Store in memory cache
        self.memory_cache[cache_key] = contexts
        
        # Store in Redis if available
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key,
                    settings.CACHE_TTL,
                    str(contexts)
                )
            except redis.RedisError:
                pass
        
        # Update metrics
        CACHE_SIZE.set(self._get_cache_size())
    
    def _semantic_search(
        self,
        question: str,
        video_id: str
    ) -> Optional[List[str]]:
        """Perform semantic search for similar contexts."""
        if not self.semantic_model:
            return None
        
        # Get all cached contexts for this video
        video_contexts = [
            (k, v) for k, v in self.memory_cache.items()
            if k.startswith(f"{video_id}:")
        ]
        
        if not video_contexts:
            return None
        
        # Encode question and contexts
        question_embedding = self.semantic_model.encode(question)
        context_embeddings = [
            self.semantic_model.encode(context)
            for _, context in video_contexts
        ]
        
        # Calculate similarities
        similarities = [
            np.dot(question_embedding, context_emb) / (
                np.linalg.norm(question_embedding) *
                np.linalg.norm(context_emb)
            )
            for context_emb in context_embeddings
        ]
        
        # Get top 3 most similar contexts
        top_indices = np.argsort(similarities)[-3:][::-1]
        return [video_contexts[i][1] for i in top_indices]
    
    def _get_cache_size(self) -> int:
        """Calculate current cache size in bytes."""
        size = 0
        for key, value in self.memory_cache.items():
            size += len(str(key)) + len(str(value))
        return size
    
    def clear_cache(self, video_id: Optional[str] = None) -> None:
        """Clear cache entries, optionally filtered by video_id."""
        if video_id:
            # Clear specific video entries
            keys_to_remove = [
                k for k in self.memory_cache.keys()
                if k.startswith(f"{video_id}:")
            ]
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # Clear Redis entries if available
            if self.redis_client:
                try:
                    pattern = f"{video_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                except redis.RedisError:
                    pass
        else:
            # Clear all entries
            self.memory_cache.clear()
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                except redis.RedisError:
                    pass
        
        CACHE_SIZE.set(self._get_cache_size()) 