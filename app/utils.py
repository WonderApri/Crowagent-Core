"""
Utility functions for the Streamlit application.
"""
import re
import streamlit as st
import time
from typing import Any
import requests

# Gemini API Key Validation
# Matches the format "AIza" followed by 35 alphanumeric/hyphen/underscore characters.
# Modern keys are 39 chars total.
GEMINI_API_KEY_RE = re.compile(r"^AIza[A-Za-z0-9\-_]{35}$")
GEMINI_VALIDATION_URL = "https://generativelanguage.googleapis.com/v1/models"

def show_congratulations():
    """Displays a congratulations message and balloons."""
    st.success("Congratulations! You've successfully run the script.")
    time.sleep(1)
    st.balloons()

def _extract_uk_postcode(text: str) -> str:
    """
    Extracts the first valid UK postcode from a string.
    Returns the postcode in standard format (e.g., "SW1A 1AA") or empty string.
    """
    if not text:
        return ""
    # Regex for UK postcodes (simplified but robust for extraction)
    match = re.search(r'\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return ""

def _safe_number(value: Any, default: float = 0.0) -> float:
    """Safely converts a value to float, returning default on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _safe_nested_number(container: dict, *keys: str, default: float = 0.0) -> float:
    """Safely retrieves a nested number from a dict."""
    current = container
    for k in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(k)
    return _safe_number(current, default)

def validate_gemini_key(key: str) -> tuple[bool, str]:
    """
    Performs security, format, and live validation for a Gemini API key.

    Hardening measures:
    1. Strips leading/trailing whitespace.
    2. Forbids newline and null characters.
    3. Checks format (prefix, length, characters).
    4. Performs a live check against the Google AI API.

    Returns
    -------
    tuple[bool, str]
        (is_valid, message)
    """
    if not isinstance(key, str):
        return False, "Invalid input: Key must be a string."

    key = key.strip()

    if not key:
        return False, "API key is missing."

    if "\n" in key or "\r" in key:
        return False, "Key contains invalid line break characters."

    if "\x00" in key:
        return False, "Key contains invalid null bytes."

    if not key.startswith("AIza"):
        return False, "Invalid Format: Your key does not start with the required 'AIza' prefix."

    if len(key) != 39:
        return False, f"Invalid Length: The key must be 39 characters long, but yours has {len(key)}."

    if not GEMINI_API_KEY_RE.match(key):
        return False, "Invalid Characters: The key contains characters that are not allowed."

    # Live API check to verify the key is functional
    try:
        resp = requests.get(
            GEMINI_VALIDATION_URL,
            headers={"x-goog-api-key": key},
            timeout=10
        )
        if resp.status_code == 200:
            return True, "API key is valid and functional."
        
        print(f"--- GEMINI VALIDATION DEBUG ---\nStatus: {resp.status_code}\nResponse: {resp.text}\n-------------------------------")

        if resp.status_code in (400, 401, 403):
            return False, "Invalid API Key: The provided key is not authorized. Please check the key and try again."
        else:
            return False, f"API key validation failed with status {resp.status_code}. Please ensure it is correct and has the necessary permissions."

    except requests.exceptions.Timeout:
        return False, "Validation timed out. Could not contact Google's authentication server."
    except requests.exceptions.RequestException as e:
        return False, f"A network error occurred during validation: {e}"

    return False, "An unknown error occurred during key validation."
