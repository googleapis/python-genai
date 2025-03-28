import pytest
from src.video_transcript_analysis.core.transcript_processor import TranscriptProcessor, TranscriptChunk

@pytest.fixture
def processor():
    return TranscriptProcessor()

@pytest.fixture
def sample_transcript():
    return """[00:00] Introduction to the video
[00:05] Welcome to our tutorial on Python programming
[00:10] In this video, we'll cover basic concepts
[00:15] First, let's look at variables
[00:20] Variables are containers for storing data
[00:25] Here's an example: x = 42
[00:30] Now, let's move on to functions
[00:35] Functions are reusable blocks of code
[00:40] They help organize our programs
[00:45] Let's create a simple function
[00:50] def greet(name):
[00:55]     return f"Hello, {name}!"
[01:00] That's all for this tutorial
[01:05] Thanks for watching!"""

def test_chunk_transcript(processor, sample_transcript):
    """Test transcript chunking functionality."""
    chunks = processor.chunk_transcript(sample_transcript)
    
    # Verify chunks are created
    assert len(chunks) > 0
    
    # Verify chunk structure
    for chunk in chunks:
        assert isinstance(chunk, TranscriptChunk)
        assert chunk.text
        assert chunk.start_line >= 0
        assert chunk.end_line >= chunk.start_line
        assert chunk.token_count > 0

def test_parse_timestamps(processor):
    """Test timestamp parsing with various formats."""
    test_cases = [
        ("[00:00] Hello", {"start_time": "00:00", "end_time": None}),
        ("[00:05-00:10] World", {"start_time": "00:05", "end_time": "00:10"}),
        ("No timestamp here", {"start_time": None, "end_time": None}),
        ("[01:30] Multiple [02:00] timestamps", {"start_time": "01:30", "end_time": None}),
    ]
    
    for line, expected in test_cases:
        result = processor.parse_timestamps(line)
        assert result == expected

def test_chunk_size_limits(processor):
    """Test that chunks respect size limits."""
    # Create a transcript with known token count
    long_text = "word " * 1000  # Creates a text with 1000 words
    chunks = processor.chunk_transcript(long_text)
    
    for chunk in chunks:
        assert chunk.token_count <= processor.settings.MAX_CHUNK_SIZE

def test_semantic_similarity(processor):
    """Test semantic similarity calculation."""
    text1 = "Python is a programming language"
    text2 = "Python is a coding language"
    text3 = "The weather is nice today"
    
    # Similar texts should have higher similarity
    sim1 = processor.get_semantic_similarity(text1, text2)
    sim2 = processor.get_semantic_similarity(text1, text3)
    
    assert sim1 > sim2

def test_empty_transcript(processor):
    """Test handling of empty transcript."""
    chunks = processor.chunk_transcript("")
    assert len(chunks) == 0

def test_whitespace_handling(processor):
    """Test handling of whitespace in transcript."""
    transcript = """
    [00:00] Line 1
    
    [00:05] Line 2
    
    [00:10] Line 3
    """
    chunks = processor.chunk_transcript(transcript)
    
    # Verify whitespace is handled properly
    for chunk in chunks:
        assert chunk.text.strip()
        assert not chunk.text.startswith("\n")
        assert not chunk.text.endswith("\n")

def test_timestamp_consistency(processor, sample_transcript):
    """Test timestamp consistency across chunks."""
    chunks = processor.chunk_transcript(sample_transcript)
    
    # Verify timestamps are in order
    for i in range(len(chunks) - 1):
        current_end = chunks[i].end_time
        next_start = chunks[i + 1].start_time
        
        if current_end and next_start:
            # Convert timestamps to seconds for comparison
            current_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(current_end.split(":"))))
            next_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(next_start.split(":"))))
            
            assert current_seconds <= next_seconds

def test_chunk_overlap(processor):
    """Test that chunks maintain proper overlap."""
    # Create a transcript that should result in overlapping chunks
    transcript = "word " * 2000  # Creates a text that should result in multiple chunks
    chunks = processor.chunk_transcript(transcript)
    
    # Verify overlap between consecutive chunks
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Check if there's overlap in the text
        current_end = current_chunk.text[-100:]  # Last 100 characters
        next_start = next_chunk.text[:100]  # First 100 characters
        
        # Verify overlap exists
        assert any(word in next_start for word in current_end.split())

def test_special_characters(processor):
    """Test handling of special characters in transcript."""
    transcript = """[00:00] Special chars: !@#$%^&*()
[00:05] Unicode: 你好世界
[00:10] Emojis: 😀 🌟 💡
[00:15] Mixed: Hello 你好! 😀"""
    
    chunks = processor.chunk_transcript(transcript)
    
    # Verify chunks are created without errors
    assert len(chunks) > 0
    
    # Verify special characters are preserved
    for chunk in chunks:
        assert chunk.text
        assert isinstance(chunk.text, str) 