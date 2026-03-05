import pytest
import streamlit as st
from core.agent import build_system_prompt

# Mock portfolio data
@pytest.fixture
def populated_portfolio():
    return [
        {'name': 'Building A', 'floor_area_m2': 1000, 'baseline_energy_mwh': 50000},
        {'name': 'Building B', 'floor_area_m2': 2500, 'baseline_energy_mwh': 120000},
    ]

@pytest.fixture
def empty_portfolio():
    return []

def test_build_system_prompt_with_populated_portfolio(populated_portfolio):
    """
    Verifies that the system prompt is correctly built with a populated portfolio,
    calculating totals and including all required instructional sections without errors.
    """
    segment = "University / Higher Education"
    try:
        prompt = build_system_prompt(populated_portfolio, segment)
    except KeyError as e:
        pytest.fail(f"Populated portfolio test failed with KeyError: {e}")

    # Check for calculated totals
    assert "- **Total Floor Area:** 3,500 m²" in prompt
    assert "- **Total Baseline Energy:** 170,000 MWh/yr" in prompt

    # Check for key instructions
    assert "## AI Capabilities" in prompt
    assert "Your advice **MUST** be strictly tailored to the user's active segment: **'University / Higher Education'**" in prompt
    assert "you **MUST** provide a valid, official external URL" in prompt
    assert "You **MUST NOT** invent, estimate, or assume any quantitative data" in prompt
    assert "Building A" in prompt
    assert "Building B" in prompt

def test_build_system_prompt_with_empty_portfolio(empty_portfolio):
    """
    Verifies that the system prompt handles an empty portfolio gracefully,
    displaying correct zero totals and not raising any errors.
    """
    segment = "Commercial Landlord"
    try:
        prompt = build_system_prompt(empty_portfolio, segment)
    except KeyError as e:
        pytest.fail(f"Empty portfolio test failed with KeyError: {e}")

    # Check for graceful handling of empty portfolio
    assert "**Portfolio Summary:**\n- No assets have been loaded. The portfolio is empty." in prompt

    # Check for other key instructions
    assert "## AI Capabilities" in prompt
    assert "Your advice **MUST** be strictly tailored to the user's active segment: **'Commercial Landlord'**" in prompt
    assert "you **MUST** provide a valid, official external URL" in prompt
    assert "You **MUST NOT** invent, estimate, or assume any quantitative data" in prompt
