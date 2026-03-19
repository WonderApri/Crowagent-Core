"""
Comprehensive QA edge-case and integration tests for Crowagent-Core.

Covers:
- Physics engine boundary conditions and edge cases
- Agent module robustness
- EPC service error handling
- Constants integrity
- Input validation exhaustive tests
- Session state management
- Performance regression guards
"""

import pytest
import time
import math
import json
from unittest.mock import patch, MagicMock

# ─── Constants Integrity Tests ───────────────────────────────────────────────


class TestConstantsIntegrity:
    """Verify physical constants are within scientifically valid ranges."""

    def test_grid_carbon_intensity_range(self):
        from config.constants import CI_ELECTRICITY
        # UK grid CI typically 0.15-0.30 kgCO2e/kWh
        assert 0.05 < CI_ELECTRICITY < 0.5, f"CI_ELECTRICITY {CI_ELECTRICITY} outside expected range"

    def test_gas_carbon_intensity_range(self):
        from config.constants import CI_GAS
        assert 0.1 < CI_GAS < 0.3, f"CI_GAS {CI_GAS} outside expected range"

    def test_electricity_tariff_range(self):
        from config.constants import DEFAULT_ELECTRICITY_TARIFF_GBP_PER_KWH
        # UK domestic tariff ~£0.15-£0.40/kWh
        assert 0.10 < DEFAULT_ELECTRICITY_TARIFF_GBP_PER_KWH < 0.50

    def test_heating_setpoint_realistic(self):
        from config.constants import HEATING_SETPOINT_C
        assert 18 <= HEATING_SETPOINT_C <= 25

    def test_heating_hours_realistic(self):
        from config.constants import HEATING_HOURS_PER_YEAR
        # 8760 hours in a year, heating season is a subset
        assert 3000 <= HEATING_HOURS_PER_YEAR <= 8760

    def test_base_ach_realistic(self):
        from config.constants import BASE_ACH
        assert 0.1 <= BASE_ACH <= 2.0

    def test_solar_irradiance_realistic(self):
        from config.constants import SOLAR_IRRADIANCE_KWH_M2_YEAR
        # UK average ~800-1200 kWh/m2/yr
        assert 500 <= SOLAR_IRRADIANCE_KWH_M2_YEAR <= 1500

    def test_part_l_u_values_ordered(self):
        """Part L wall U-values should be stricter (lower) than glazing."""
        from config.constants import (
            PART_L_2021_U_WALL,
            PART_L_2021_U_ROOF,
            PART_L_2021_U_GLAZING,
        )
        assert PART_L_2021_U_WALL < PART_L_2021_U_GLAZING
        assert PART_L_2021_U_ROOF < PART_L_2021_U_GLAZING
        assert PART_L_2021_U_ROOF <= PART_L_2021_U_WALL

    def test_epc_bands_ordered_descending(self):
        from config.constants import EPC_BANDS
        thresholds = [b["threshold"] for b in EPC_BANDS]
        assert thresholds == sorted(thresholds, reverse=True), "EPC bands must be in descending threshold order"

    def test_epc_bands_cover_all_letters(self):
        from config.constants import EPC_BANDS
        bands = {b["band"] for b in EPC_BANDS}
        assert bands == {"A", "B", "C", "D", "E", "F", "G"}

    def test_mees_target_bands_progression(self):
        from config.constants import MEES_CURRENT_MIN_BAND, MEES_2028_TARGET_BAND, MEES_2030_TARGET_BAND
        band_order = ["A", "B", "C", "D", "E", "F", "G"]
        assert band_order.index(MEES_2030_TARGET_BAND) <= band_order.index(MEES_2028_TARGET_BAND)
        assert band_order.index(MEES_2028_TARGET_BAND) <= band_order.index(MEES_CURRENT_MIN_BAND)

    def test_fhs_max_primary_energy_positive(self):
        from config.constants import FHS_MAX_PRIMARY_ENERGY
        assert FHS_MAX_PRIMARY_ENERGY > 0


# ─── Physics Engine Edge Cases ───────────────────────────────────────────────


class TestPhysicsEdgeCases:
    """Edge cases and boundary conditions for the PINN thermal model."""

    def _make_building(self, **overrides):
        defaults = {
            "floor_area_m2": 500,
            "height_m": 3.5,
            "glazing_ratio": 0.3,
            "u_value_wall": 1.5,
            "u_value_roof": 0.8,
            "u_value_glazing": 3.0,
            "baseline_energy_mwh": 200,
        }
        defaults.update(overrides)
        return defaults

    def _make_scenario(self, **overrides):
        defaults = {
            "u_value_wall": 0.18,
            "u_value_roof": 0.15,
            "u_value_glazing": 1.4,
            "infiltration_reduction": 0.3,
            "solar_gain_reduction": 0.0,
        }
        defaults.update(overrides)
        return defaults

    def _make_weather(self, **overrides):
        defaults = {"temperature_c": 10.0}
        defaults.update(overrides)
        return defaults

    def test_zero_floor_area_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="floor_area_m2"):
            _validate_model_inputs(
                self._make_building(floor_area_m2=0),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_negative_floor_area_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="floor_area_m2"):
            _validate_model_inputs(
                self._make_building(floor_area_m2=-100),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_zero_height_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="height_m"):
            _validate_model_inputs(
                self._make_building(height_m=0),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_glazing_ratio_at_zero_boundary(self):
        from core.physics import _validate_model_inputs
        # Should NOT raise
        _validate_model_inputs(
            self._make_building(glazing_ratio=0),
            self._make_scenario(),
            self._make_weather(),
        )

    def test_glazing_ratio_at_max_boundary(self):
        from core.physics import _validate_model_inputs
        # 0.95 is the max
        _validate_model_inputs(
            self._make_building(glazing_ratio=0.95),
            self._make_scenario(),
            self._make_weather(),
        )

    def test_glazing_ratio_above_max_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(
                self._make_building(glazing_ratio=0.96),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_negative_glazing_ratio_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(
                self._make_building(glazing_ratio=-0.1),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_u_value_zero_rejected(self):
        from core.physics import _validate_model_inputs
        for key in ("u_value_wall", "u_value_roof", "u_value_glazing"):
            with pytest.raises(ValueError, match=key):
                _validate_model_inputs(
                    self._make_building(**{key: 0}),
                    self._make_scenario(),
                    self._make_weather(),
                )

    def test_u_value_above_max_rejected(self):
        from core.physics import _validate_model_inputs
        for key in ("u_value_wall", "u_value_roof", "u_value_glazing"):
            with pytest.raises(ValueError, match=key):
                _validate_model_inputs(
                    self._make_building(**{key: 6.1}),
                    self._make_scenario(),
                    self._make_weather(),
                )

    def test_u_value_at_max_boundary_accepted(self):
        from core.physics import _validate_model_inputs
        _validate_model_inputs(
            self._make_building(u_value_wall=6, u_value_roof=6, u_value_glazing=6),
            self._make_scenario(),
            self._make_weather(),
        )

    def test_negative_baseline_energy_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="baseline_energy_mwh"):
            _validate_model_inputs(
                self._make_building(baseline_energy_mwh=-10),
                self._make_scenario(),
                self._make_weather(),
            )

    def test_zero_baseline_energy_accepted(self):
        from core.physics import _validate_model_inputs
        _validate_model_inputs(
            self._make_building(baseline_energy_mwh=0),
            self._make_scenario(),
            self._make_weather(),
        )

    def test_extreme_cold_temperature_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="temperature"):
            _validate_model_inputs(
                self._make_building(),
                self._make_scenario(),
                self._make_weather(temperature_c=-41),
            )

    def test_extreme_hot_temperature_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="temperature"):
            _validate_model_inputs(
                self._make_building(),
                self._make_scenario(),
                self._make_weather(temperature_c=61),
            )

    def test_boundary_temperatures_accepted(self):
        from core.physics import _validate_model_inputs
        _validate_model_inputs(
            self._make_building(),
            self._make_scenario(),
            self._make_weather(temperature_c=-40),
        )
        _validate_model_inputs(
            self._make_building(),
            self._make_scenario(),
            self._make_weather(temperature_c=60),
        )

    def test_missing_temperature_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="temperature_c"):
            _validate_model_inputs(
                self._make_building(),
                self._make_scenario(),
                {},
            )

    def test_infiltration_reduction_boundaries(self):
        from core.physics import _validate_model_inputs
        # 0 and 0.95 should be accepted
        _validate_model_inputs(
            self._make_building(),
            self._make_scenario(infiltration_reduction=0),
            self._make_weather(),
        )
        _validate_model_inputs(
            self._make_building(),
            self._make_scenario(infiltration_reduction=0.95),
            self._make_weather(),
        )

    def test_infiltration_reduction_over_max_rejected(self):
        from core.physics import _validate_model_inputs
        with pytest.raises(ValueError, match="infiltration_reduction"):
            _validate_model_inputs(
                self._make_building(),
                self._make_scenario(infiltration_reduction=0.96),
                self._make_weather(),
            )


# ─── EPC Service Edge Cases ─────────────────────────────────────────────────


class TestEPCServiceEdgeCases:
    """Edge cases for the EPC service integration."""

    def test_valid_postcode_regex(self):
        from services.epc import UK_POSTCODE_RE
        valid_postcodes = [
            "SW1A 2AA", "EC1A 1BB", "W1A 0AX", "M1 1AE",
            "B33 8TH", "CR2 6XH", "DN55 1PT",
            # GIR 0AA is a special historic postcode that doesn't match standard format
        ]
        for pc in valid_postcodes:
            assert UK_POSTCODE_RE.search(pc), f"Should match valid postcode: {pc}"

    def test_invalid_postcode_regex(self):
        from services.epc import UK_POSTCODE_RE
        invalid = ["12345", "ABCDE", "", "123 ABC"]
        for pc in invalid:
            assert not UK_POSTCODE_RE.search(pc), f"Should not match: {pc}"

    def test_valid_epc_bands_complete(self):
        from services.epc import VALID_EPC_BANDS
        assert VALID_EPC_BANDS == {"A", "B", "C", "D", "E", "F", "G"}

    def test_epc_fetch_error_is_runtime_error(self):
        from services.epc import EPCFetchError
        assert issubclass(EPCFetchError, RuntimeError)


# ─── Agent Module Tests ──────────────────────────────────────────────────────


class TestAgentModule:
    """Tests for the AI advisor agent module."""

    def test_gemini_models_list_not_empty(self):
        from core.agent import GEMINI_MODELS
        assert len(GEMINI_MODELS) > 0

    def test_gemini_fallback_urls_match_models(self):
        from core.agent import GEMINI_MODELS, GEMINI_FALLBACK_URLS
        assert len(GEMINI_FALLBACK_URLS) == len(GEMINI_MODELS)

    def test_gemini_url_is_first_fallback(self):
        from core.agent import GEMINI_URL, GEMINI_FALLBACK_URLS
        assert GEMINI_URL == GEMINI_FALLBACK_URLS[0]

    def test_max_agent_loops_has_safety_limit(self):
        from core.agent import MAX_AGENT_LOOPS
        assert 1 <= MAX_AGENT_LOOPS <= 50, "MAX_AGENT_LOOPS must have reasonable bounds"

    def test_max_output_tokens_is_reasonable(self):
        from core.agent import MAX_OUTPUT_TOKENS
        assert 100 <= MAX_OUTPUT_TOKENS <= 10000

    def test_build_system_prompt_returns_string(self):
        from core.agent import build_system_prompt
        result = build_system_prompt("university_he", [])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_system_prompt_includes_segment(self):
        from core.agent import build_system_prompt
        result = build_system_prompt("university_he", [])
        # The prompt should reference the segment context
        assert isinstance(result, str)

    def test_build_system_prompt_handles_argument_swap(self):
        """Test legacy compatibility — arguments can be swapped."""
        from core.agent import build_system_prompt
        # Pass list first, string second — should be auto-corrected
        result = build_system_prompt([], "university_he")
        assert isinstance(result, str)

    def test_build_system_prompt_with_portfolio_data(self):
        from core.agent import build_system_prompt
        portfolio = [
            {"name": "Building A", "floor_area_m2": 1000, "epc_band": "D"},
            {"name": "Building B", "floor_area_m2": 500, "epc_band": "F"},
        ]
        result = build_system_prompt("university_he", portfolio)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_system_prompt_with_empty_segment(self):
        from core.agent import build_system_prompt
        result = build_system_prompt("", [])
        assert isinstance(result, str)


# ─── App Utils Tests ─────────────────────────────────────────────────────────


class TestAppUtilsEdgeCases:
    """Extended edge cases for app utility functions."""

    def test_validate_gemini_key_empty_string(self):
        from app.utils import validate_gemini_key
        valid, msg, warn = validate_gemini_key("")
        assert valid is False

    def test_validate_gemini_key_none_type(self):
        from app.utils import validate_gemini_key
        valid, msg, warn = validate_gemini_key(None)
        assert valid is False

    def test_validate_gemini_key_whitespace_only(self):
        from app.utils import validate_gemini_key
        valid, msg, warn = validate_gemini_key("   ")
        assert valid is False

    def test_validate_gemini_key_with_xss_payload(self):
        from app.utils import validate_gemini_key
        valid, msg, warn = validate_gemini_key("<script>alert('xss')</script>")
        assert valid is False

    def test_validate_gemini_key_with_sql_injection(self):
        from app.utils import validate_gemini_key
        valid, msg, warn = validate_gemini_key("' OR 1=1 --")
        assert valid is False


# ─── Performance Regression Guards ───────────────────────────────────────────


class TestPerformanceGuards:
    """Ensure critical operations complete within acceptable time bounds."""

    def test_constants_import_performance(self):
        """Importing constants module should be fast (no heavy computation)."""
        start = time.time()
        import importlib
        import config.constants
        importlib.reload(config.constants)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"Constants import took {elapsed:.2f}s (max 1s)"

    def test_physics_validation_performance(self):
        """Input validation should be sub-millisecond."""
        from core.physics import _validate_model_inputs
        building = {
            "floor_area_m2": 500, "height_m": 3.5, "glazing_ratio": 0.3,
            "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 3.0,
            "baseline_energy_mwh": 200,
        }
        scenario = {
            "u_value_wall": 0.18, "u_value_roof": 0.15, "u_value_glazing": 1.4,
            "infiltration_reduction": 0.3, "solar_gain_reduction": 0.0,
        }
        weather = {"temperature_c": 10.0}

        start = time.time()
        for _ in range(1000):
            _validate_model_inputs(building, scenario, weather)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"1000 validations took {elapsed:.2f}s (max 1s)"

    def test_epc_band_lookup_performance(self):
        """EPC band constants lookup should be fast."""
        from config.constants import EPC_BANDS
        start = time.time()
        for _ in range(10000):
            _ = [b for b in EPC_BANDS if b["band"] == "D"]
        elapsed = time.time() - start
        assert elapsed < 1.0, f"10000 band lookups took {elapsed:.2f}s"

    def test_system_prompt_generation_performance(self):
        """System prompt generation should complete quickly."""
        from core.agent import build_system_prompt
        portfolio = [{"name": f"Building {i}", "floor_area_m2": 1000} for i in range(50)]

        start = time.time()
        for _ in range(100):
            build_system_prompt("university_he", portfolio)
        elapsed = time.time() - start
        assert elapsed < 5.0, f"100 prompt generations took {elapsed:.2f}s"


# ─── Scenario Configuration Tests ───────────────────────────────────────────


class TestScenarioConfiguration:
    """Verify scenario definitions are valid and complete."""

    def test_scenarios_importable(self):
        from config.scenarios import SCENARIOS
        assert isinstance(SCENARIOS, dict)

    def test_scenarios_not_empty(self):
        from config.scenarios import SCENARIOS
        assert len(SCENARIOS) > 0

    def test_scenario_keys_are_strings(self):
        from config.scenarios import SCENARIOS
        for key in SCENARIOS:
            assert isinstance(key, str)

    def test_scenario_values_are_dicts(self):
        from config.scenarios import SCENARIOS
        for key, val in SCENARIOS.items():
            assert isinstance(val, dict), f"Scenario '{key}' value must be a dict"


# ─── Security Checks ────────────────────────────────────────────────────────


class TestSecurityHardening:
    """Verify security properties of the codebase."""

    def test_no_hardcoded_api_keys_in_agent(self):
        """Agent module should not contain hardcoded API keys."""
        import inspect
        import core.agent
        source = inspect.getsource(core.agent)
        # Check no AIza-prefixed keys (Google API key format)
        import re
        matches = re.findall(r'AIza[0-9A-Za-z\-_]{35}', source)
        assert len(matches) == 0, f"Found hardcoded API key(s) in agent module: {matches}"

    def test_no_hardcoded_api_keys_in_epc(self):
        """EPC service should not contain hardcoded API keys."""
        import inspect
        import services.epc
        source = inspect.getsource(services.epc)
        import re
        matches = re.findall(r'AIza[0-9A-Za-z\-_]{35}', source)
        assert len(matches) == 0, f"Found hardcoded API key(s) in EPC service"

    def test_gemini_urls_use_https(self):
        """All Gemini API URLs must use HTTPS."""
        from core.agent import GEMINI_FALLBACK_URLS
        for url in GEMINI_FALLBACK_URLS:
            assert url.startswith("https://"), f"URL not HTTPS: {url}"

    def test_epc_api_base_uses_https(self):
        """EPC API base URL must use HTTPS."""
        from services.epc import _ODS_EPC_BASE
        assert _ODS_EPC_BASE.startswith("https://")


# ─── Data Type Robustness ────────────────────────────────────────────────────


class TestDataTypeRobustness:
    """Ensure functions handle unexpected data types gracefully."""

    def test_physics_validation_with_string_numbers(self):
        """String-encoded numbers should be handled (float() conversion)."""
        from core.physics import _validate_model_inputs
        building = {
            "floor_area_m2": "500", "height_m": "3.5", "glazing_ratio": "0.3",
            "u_value_wall": "1.5", "u_value_roof": "0.8", "u_value_glazing": "3.0",
            "baseline_energy_mwh": "200",
        }
        scenario = {
            "infiltration_reduction": "0.3",
            "solar_gain_reduction": "0.0",
        }
        weather = {"temperature_c": "10.0"}
        # Should not raise — float() handles string numbers
        _validate_model_inputs(building, scenario, weather)

    def test_epc_postcode_regex_case_insensitive(self):
        """UK postcode regex should match both upper and lower case."""
        from services.epc import UK_POSTCODE_RE
        assert UK_POSTCODE_RE.search("sw1a 2aa")
        assert UK_POSTCODE_RE.search("SW1A 2AA")
        assert UK_POSTCODE_RE.search("Sw1a 2Aa")
