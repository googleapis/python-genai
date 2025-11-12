#!/usr/bin/env python3
"""
Unit test to verify the _ensure_file_active and _process_contents_for_generation functions.

This tests the core logic of the fix without requiring actual API calls.
"""

import sys
from unittest.mock import Mock, patch, MagicMock
from google.genai import types, errors
from google.genai.models import _ensure_file_active, _process_contents_for_generation


def test_ensure_file_active_already_active():
    """Test that ACTIVE files are returned immediately."""
    print("\n" + "="*70)
    print("TEST: File already in ACTIVE state")
    print("="*70)
    
    # Create a mock file that's already ACTIVE
    mock_file = Mock(spec=types.File)
    mock_file.name = "files/test-video-123"
    mock_file.state = types.FileState.ACTIVE
    
    mock_api_client = Mock()
    
    # Call the function
    result = _ensure_file_active(mock_api_client, mock_file)
    
    # Should return immediately without API calls
    assert result == mock_file
    assert not mock_api_client.request.called
    
    print("✅ PASSED: ACTIVE file returned immediately without polling")


def test_ensure_file_active_processing_state():
    """Test that PROCESSING files trigger polling."""
    print("\n" + "="*70)
    print("TEST: File in PROCESSING state (should poll)")
    print("="*70)
    
    # Create a mock file that's PROCESSING
    mock_file = Mock(spec=types.File)
    mock_file.name = "files/test-video-123"
    mock_file.state = types.FileState.PROCESSING
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Mock the response - file becomes ACTIVE after first check
    mock_response = Mock()
    mock_response.body = '{"name": "files/test-video-123", "state": "ACTIVE"}'
    mock_api_client.request.return_value = mock_response
    
    # Mock the File._from_response to return an ACTIVE file
    with patch.object(types.File, '_from_response') as mock_from_response:
        active_file = Mock(spec=types.File)
        active_file.state = types.FileState.ACTIVE
        active_file.name = "files/test-video-123"
        mock_from_response.return_value = active_file
        
        with patch('time.sleep'):  # Skip actual sleeping in tests
            result = _ensure_file_active(mock_api_client, mock_file, max_retries=1)
        
        # Should have called the API to check file state
        assert mock_api_client.request.called
        assert result.state == types.FileState.ACTIVE
    
    print("✅ PASSED: PROCESSING file triggered polling and became ACTIVE")


def test_ensure_file_active_failed_state():
    """Test that FAILED files raise FileProcessingError."""
    print("\n" + "="*70)
    print("TEST: File in FAILED state (should raise error)")
    print("="*70)
    
    # Create a mock file that's PROCESSING
    mock_file = Mock(spec=types.File)
    mock_file.name = "files/test-video-123"
    mock_file.state = types.FileState.PROCESSING
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Mock the response - file is FAILED
    mock_response = Mock()
    mock_response.body = '{"name": "files/test-video-123", "state": "FAILED"}'
    mock_api_client.request.return_value = mock_response
    
    # Mock the File._from_response to return a FAILED file
    with patch.object(types.File, '_from_response') as mock_from_response:
        failed_file = Mock(spec=types.File)
        failed_file.state = types.FileState.FAILED
        failed_file.error = Mock()
        failed_file.error.message = "Processing failed"
        mock_from_response.return_value = failed_file
        
        try:
            with patch('time.sleep'):  # Skip actual sleeping
                _ensure_file_active(mock_api_client, mock_file, max_retries=1)
            assert False, "Should have raised FileProcessingError"
        except errors.FileProcessingError as e:
            print(f"✅ PASSED: Correctly raised FileProcessingError: {e}")


def test_process_contents_with_file():
    """Test that _process_contents_for_generation processes files in contents."""
    print("\n" + "="*70)
    print("TEST: Process contents containing files")
    print("="*70)
    
    # Create mock content with a file
    mock_file = Mock(spec=types.File)
    mock_file.name = "files/test-video-123"
    mock_file.state = types.FileState.ACTIVE
    
    mock_part = Mock(spec=types.Part)
    mock_part.file_data = mock_file
    
    mock_content = Mock(spec=types.Content)
    mock_content.parts = [mock_part]
    
    mock_api_client = Mock()
    
    # Mock t_contents to return our mock content
    with patch('google.genai.models.t.t_contents') as mock_t_contents:
        mock_t_contents.return_value = [mock_content]
        
        # Process the contents
        result = _process_contents_for_generation(
            mock_api_client,
            [mock_content]
        )
        
        # Should have processed the contents
        assert len(result) == 1
        assert isinstance(result[0], Mock)
    
    print("✅ PASSED: Contents with files processed correctly")


def run_all_tests():
    """Run all unit tests."""
    print("\n" + "="*70)
    print("VIDEO FILE API FIX - UNIT TESTS")
    print("Testing _ensure_file_active and _process_contents_for_generation")
    print("="*70)
    
    try:
        test_ensure_file_active_already_active()
        test_ensure_file_active_processing_state()
        test_ensure_file_active_failed_state()
        test_process_contents_with_file()
        
        print("\n" + "="*70)
        print("✅ ALL UNIT TESTS PASSED!")
        print("="*70)
        print("\nThe fix correctly:")
        print("  ✅ Returns ACTIVE files immediately (no unnecessary delays)")
        print("  ✅ Polls for PROCESSING files until they become ACTIVE")
        print("  ✅ Raises FileProcessingError for FAILED files")
        print("  ✅ Processes file contents properly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

