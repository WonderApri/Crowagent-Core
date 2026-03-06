"""
Tests for app/utils.py
"""
import pytest
from unittest.mock import patch, Mock
import requests

# Add project root to path to allow absolute imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import validate_gemini_key

# A correctly formatted, but fake, API key
VALID_FORMAT_KEY = "AIza" + "a" * 35

class TestValidateGeminiKey:
    """Tests for the validate_gemini_key function."""

    def test_valid_key_and_api_call(self):
        """Test with a valid key that returns 200 from the API."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            is_valid, message = validate_gemini_key(VALID_FORMAT_KEY)
            assert is_valid is True
            assert message == "API key is valid and functional."
            mock_get.assert_called_once_with(
                "https://generativelanguage.googleapis.com/v1/models",
                headers={"x-goog-api-key": VALID_FORMAT_KEY},
                timeout=10
            )

    def test_invalid_key_401_response(self):
        """Test with a key that is rejected by the API (401)."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response

            is_valid, message = validate_gemini_key(VALID_FORMAT_KEY)
            assert is_valid is False
            assert "Invalid API Key" in message

    def test_api_error_other_status_code(self):
        """Test with an API call that returns a non-200/401 status code."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            is_valid, message = validate_gemini_key(VALID_FORMAT_KEY)
            assert is_valid is False
            assert "failed with status 500" in message

    def test_request_timeout(self):
        """Test the behavior on a request timeout."""
        with patch('requests.get', side_effect=requests.exceptions.Timeout) as mock_get:
            is_valid, message = validate_gemini_key(VALID_FORMAT_KEY)
            assert is_valid is False
            assert "Validation timed out" in message

    def test_request_exception(self):
        """Test the behavior on a generic request exception."""
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")) as mock_get:
            is_valid, message = validate_gemini_key(VALID_FORMAT_KEY)
            assert is_valid is False
            assert "A network error occurred" in message

    def test_key_with_whitespace(self):
        """Test that leading/trailing whitespace is stripped correctly."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            is_valid, message = validate_gemini_key(f"  {VALID_FORMAT_KEY}  ")
            assert is_valid is True
            mock_get.assert_called_once_with(
                "https://generativelanguage.googleapis.com/v1/models",
                headers={"x-goog-api-key": VALID_FORMAT_KEY}, # Key should be stripped
                timeout=10
            )

    def test_key_too_short(self):
        """Test a key that is too short."""
        is_valid, message = validate_gemini_key("AIza12345")
        assert is_valid is False
        assert "Invalid Length" in message

    def test_key_too_long(self):
        """Test a key that is too long."""
        is_valid, message = validate_gemini_key(VALID_FORMAT_KEY + "x")
        assert is_valid is False
        assert "Invalid Length" in message

    def test_key_wrong_prefix(self):
        """Test a key with the wrong prefix."""
        is_valid, message = validate_gemini_key("Aiza" + "a" * 35) # Lowercase 'i'
        assert is_valid is False
        assert "does not start with the required 'AIza' prefix" in message

    def test_key_with_invalid_characters(self):
        """Test a key with invalid characters."""
        is_valid, message = validate_gemini_key("AIza" + "!" * 35)
        assert is_valid is False
        assert "Invalid Characters" in message

    def test_empty_key(self):
        """Test an empty string as a key."""
        is_valid, message = validate_gemini_key("")
        assert is_valid is False
        assert "API key is missing" in message

    def test_none_key(self):
        """Test None as a key."""
        is_valid, message = validate_gemini_key(None)
        assert is_valid is False
        assert "Invalid input: Key must be a string." in message
