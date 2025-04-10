from typing import List, Dict, Optional
import re
import tiktoken
import nltk
from textstat import textstat
from dataclasses import dataclass
from ..config.settings import settings

@dataclass
class TranscriptChunk:
    """Represents a chunk of transcript with metadata."""
    text: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    token_count: int = 0

class TranscriptProcessor:
    """Processes and chunks video transcripts with semantic awareness."""
    
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def chunk_transcript(self, text: str) -> List[TranscriptChunk]:
        """Implement hybrid chunking with semantic and fixed-length approaches."""
        chunks: List[TranscriptChunk] = []
        lines = text.split('\n')
        current_chunk = []
        current_tokens = 0
        line_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse timestamps if present
            timestamp_info = self.parse_timestamps(line)
            line_tokens = len(self.tokenizer.encode(line))
            
            # Check if adding this line would exceed max chunk size
            if current_tokens + line_tokens > settings.MAX_CHUNK_SIZE:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, line_number - len(current_chunk)))
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append(line)
            current_tokens += line_tokens
            line_number += 1
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, line_number - len(current_chunk)))
        
        return chunks
    
    def parse_timestamps(self, line: str) -> Dict[str, Optional[str]]:
        """Parse various timestamp formats from transcript lines."""
        # HH:MM-HH:MM format
        time_range_pattern = r'(\d{2}:\d{2})-(\d{2}:\d{2})'
        # [HH:MM] format
        single_time_pattern = r'\[(\d{2}:\d{2})\]'
        
        time_range_match = re.search(time_range_pattern, line)
        single_time_match = re.search(single_time_pattern, line)
        
        if time_range_match:
            return {
                'start_time': time_range_match.group(1),
                'end_time': time_range_match.group(2)
            }
        elif single_time_match:
            return {
                'start_time': single_time_match.group(1),
                'end_time': None
            }
        
        return {'start_time': None, 'end_time': None}
    
    def _create_chunk(self, lines: List[str], start_line: int) -> TranscriptChunk:
        """Create a TranscriptChunk from a list of lines."""
        text = '\n'.join(lines)
        token_count = len(self.tokenizer.encode(text))
        
        # Extract timestamps from first and last lines
        first_timestamps = self.parse_timestamps(lines[0])
        last_timestamps = self.parse_timestamps(lines[-1])
        
        return TranscriptChunk(
            text=text,
            start_time=first_timestamps['start_time'],
            end_time=last_timestamps['end_time'] or first_timestamps['end_time'],
            start_line=start_line,
            end_line=start_line + len(lines) - 1,
            token_count=token_count
        )
    
    def get_semantic_similarity(self, chunk1: str, chunk2: str) -> float:
        """Calculate semantic similarity between two chunks using textstat."""
        # This is a simple implementation - could be enhanced with more sophisticated
        # semantic similarity measures like cosine similarity with embeddings
        return textstat.sentence_similarity(chunk1, chunk2) 