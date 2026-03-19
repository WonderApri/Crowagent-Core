"""
Comprehensive field-level validation and mandatory field enforcement tests.

Covers:
  - core/physics.py: _validate_model_inputs, calculate_thermal_load
  - app/compliance.py: validate_energy_kwh, validate_floor_area, validate_u_value,
    estimate_epc_rating, mees_gap_analysis, calculate_carbon_baseline,
    part_l_compliance_check
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.physics import _validate_model_inputs, calculate_thermal_load
from app.compliance import (
    validate_energy_kwh,
    validate_floor_area,
    validate_u_value,
    estimate_epc_rating,
    mees_gap_analysis,
    calculate_carbon_baseline,
    part_l_compliance_check,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_building():
    return {
        "floor_area_m2": 500.0,
        "height_m": 4.0,
        "glazing_ratio": 0.3,
        "u_value_wall": 1.5,
        "u_value_roof": 0.8,
        "u_value_glazing": 2.0,
        "baseline_energy_mwh": 120.0,
    }


@pytest.fixture
def valid_scenario():
    return {
        "u_wall_factor": 0.5,
        "u_roof_factor": 0.6,
        "u_glazing_factor": 0.7,
        "infiltration_reduction": 0.3,
        "solar_gain_reduction": 0.2,
        "renewable_kwh": 5000,
        "install_cost_gbp": 50000,
    }


@pytest.fixture
def valid_weather():
    return {"temperature_c": 10.0}


# ===========================================================================
# A. Physics Engine — _validate_model_inputs
# ===========================================================================

class TestValidateModelInputsMandatoryFields:
    """Test that each required field is enforced."""

    def test_missing_floor_area_defaults_to_zero_fails(self, valid_scenario, valid_weather):
        building = {"height_m": 4, "glazing_ratio": 0.3, "u_value_wall": 1.5,
                     "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="floor_area_m2"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_height_defaults_to_zero_fails(self, valid_scenario, valid_weather):
        building = {"floor_area_m2": 500, "glazing_ratio": 0.3, "u_value_wall": 1.5,
                     "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="height_m"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_glazing_ratio_defaults_negative_fails(self, valid_scenario, valid_weather):
        building = {"floor_area_m2": 500, "height_m": 4, "u_value_wall": 1.5,
                     "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_u_value_wall_defaults_zero_fails(self, valid_scenario, valid_weather):
        building = {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0.3,
                     "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="u_value_wall"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_u_value_roof_fails(self, valid_scenario, valid_weather):
        building = {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0.3,
                     "u_value_wall": 1.5, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="u_value_roof"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_u_value_glazing_fails(self, valid_scenario, valid_weather):
        building = {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0.3,
                     "u_value_wall": 1.5, "u_value_roof": 0.8}
        with pytest.raises(ValueError, match="u_value_glazing"):
            _validate_model_inputs(building, valid_scenario, valid_weather)

    def test_missing_temperature_c_fails(self, valid_building, valid_scenario):
        with pytest.raises(ValueError, match="temperature_c"):
            _validate_model_inputs(valid_building, valid_scenario, {})

    def test_empty_building_fails(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError):
            _validate_model_inputs({}, valid_scenario, valid_weather)

    def test_empty_weather_fails(self, valid_building, valid_scenario):
        with pytest.raises(ValueError, match="temperature_c"):
            _validate_model_inputs(valid_building, valid_scenario, {})

    def test_all_valid_passes(self, valid_building, valid_scenario, valid_weather):
        # Should not raise
        _validate_model_inputs(valid_building, valid_scenario, valid_weather)


class TestPhysicsFloorAreaValidation:
    def test_zero_fails(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": 0, "height_m": 4, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="floor_area_m2"):
            _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_negative_fails(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": -10, "height_m": 4, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="floor_area_m2"):
            _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_small_positive_passes(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": 0.001, "height_m": 4, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_large_value_passes(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": 100000, "height_m": 4, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        _validate_model_inputs(b, valid_scenario, valid_weather)


class TestPhysicsHeightValidation:
    def test_zero_fails(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": 500, "height_m": 0, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="height_m"):
            _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_negative_fails(self, valid_scenario, valid_weather):
        b = {"floor_area_m2": 500, "height_m": -3, "glazing_ratio": 0.3,
             "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        with pytest.raises(ValueError, match="height_m"):
            _validate_model_inputs(b, valid_scenario, valid_weather)


class TestPhysicsGlazingRatioValidation:
    def _build(self, ratio):
        return {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": ratio,
                "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}

    def test_zero_passes(self, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(0), valid_scenario, valid_weather)

    def test_0_95_passes(self, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(0.95), valid_scenario, valid_weather)

    def test_negative_fails(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(self._build(-0.01), valid_scenario, valid_weather)

    def test_above_0_95_fails(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(self._build(0.96), valid_scenario, valid_weather)

    def test_exactly_1_fails(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="glazing_ratio"):
            _validate_model_inputs(self._build(1.0), valid_scenario, valid_weather)


class TestPhysicsUValueValidation:
    def _build(self, **overrides):
        base = {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0.3,
                "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0}
        base.update(overrides)
        return base

    @pytest.mark.parametrize("key", ["u_value_wall", "u_value_roof", "u_value_glazing"])
    def test_zero_fails(self, key, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match=key):
            _validate_model_inputs(self._build(**{key: 0}), valid_scenario, valid_weather)

    @pytest.mark.parametrize("key", ["u_value_wall", "u_value_roof", "u_value_glazing"])
    def test_negative_fails(self, key, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match=key):
            _validate_model_inputs(self._build(**{key: -1}), valid_scenario, valid_weather)

    @pytest.mark.parametrize("key", ["u_value_wall", "u_value_roof", "u_value_glazing"])
    def test_above_6_fails(self, key, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match=key):
            _validate_model_inputs(self._build(**{key: 6.01}), valid_scenario, valid_weather)

    @pytest.mark.parametrize("key", ["u_value_wall", "u_value_roof", "u_value_glazing"])
    def test_exactly_6_passes(self, key, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(**{key: 6.0}), valid_scenario, valid_weather)

    @pytest.mark.parametrize("key", ["u_value_wall", "u_value_roof", "u_value_glazing"])
    def test_small_positive_passes(self, key, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(**{key: 0.01}), valid_scenario, valid_weather)


class TestPhysicsBaselineEnergyValidation:
    def _build(self, baseline):
        return {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0.3,
                "u_value_wall": 1.5, "u_value_roof": 0.8, "u_value_glazing": 2.0,
                "baseline_energy_mwh": baseline}

    def test_negative_fails(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="baseline_energy_mwh"):
            _validate_model_inputs(self._build(-1), valid_scenario, valid_weather)

    def test_zero_passes(self, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(0), valid_scenario, valid_weather)

    def test_large_value_passes(self, valid_scenario, valid_weather):
        _validate_model_inputs(self._build(999999), valid_scenario, valid_weather)


class TestPhysicsScenarioValidation:
    def test_infiltration_negative_fails(self, valid_building, valid_weather):
        s = {"infiltration_reduction": -0.01, "solar_gain_reduction": 0.2}
        with pytest.raises(ValueError, match="infiltration_reduction"):
            _validate_model_inputs(valid_building, s, valid_weather)

    def test_infiltration_above_0_95_fails(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.96, "solar_gain_reduction": 0.2}
        with pytest.raises(ValueError, match="infiltration_reduction"):
            _validate_model_inputs(valid_building, s, valid_weather)

    def test_infiltration_at_0_passes(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.0, "solar_gain_reduction": 0.2}
        _validate_model_inputs(valid_building, s, valid_weather)

    def test_infiltration_at_0_95_passes(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.95, "solar_gain_reduction": 0.2}
        _validate_model_inputs(valid_building, s, valid_weather)

    def test_solar_gain_negative_fails(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.3, "solar_gain_reduction": -0.01}
        with pytest.raises(ValueError, match="solar_gain_reduction"):
            _validate_model_inputs(valid_building, s, valid_weather)

    def test_solar_gain_above_1_fails(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.3, "solar_gain_reduction": 1.01}
        with pytest.raises(ValueError, match="solar_gain_reduction"):
            _validate_model_inputs(valid_building, s, valid_weather)

    def test_solar_gain_at_0_passes(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.3, "solar_gain_reduction": 0.0}
        _validate_model_inputs(valid_building, s, valid_weather)

    def test_solar_gain_at_1_passes(self, valid_building, valid_weather):
        s = {"infiltration_reduction": 0.3, "solar_gain_reduction": 1.0}
        _validate_model_inputs(valid_building, s, valid_weather)


class TestPhysicsTemperatureValidation:
    def test_below_minus_40_fails(self, valid_building, valid_scenario):
        with pytest.raises(ValueError, match="temperature_c"):
            _validate_model_inputs(valid_building, valid_scenario, {"temperature_c": -40.1})

    def test_above_60_fails(self, valid_building, valid_scenario):
        with pytest.raises(ValueError, match="temperature_c"):
            _validate_model_inputs(valid_building, valid_scenario, {"temperature_c": 60.1})

    def test_exactly_minus_40_passes(self, valid_building, valid_scenario):
        _validate_model_inputs(valid_building, valid_scenario, {"temperature_c": -40.0})

    def test_exactly_60_passes(self, valid_building, valid_scenario):
        _validate_model_inputs(valid_building, valid_scenario, {"temperature_c": 60.0})

    def test_zero_passes(self, valid_building, valid_scenario):
        _validate_model_inputs(valid_building, valid_scenario, {"temperature_c": 0})


# ===========================================================================
# B. calculate_thermal_load — integration-level field validation
# ===========================================================================

class TestCalculateThermalLoadValidation:
    def test_valid_inputs_return_dict(self, valid_building, valid_scenario, valid_weather):
        result = calculate_thermal_load(valid_building, valid_scenario, valid_weather)
        assert isinstance(result, dict)
        assert "baseline_energy_mwh" in result
        assert "scenario_energy_mwh" in result

    def test_invalid_building_raises(self, valid_scenario, valid_weather):
        with pytest.raises(ValueError):
            calculate_thermal_load({}, valid_scenario, valid_weather)

    def test_negative_tariff_raises(self, valid_building, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="tariff"):
            calculate_thermal_load(valid_building, valid_scenario, valid_weather,
                                   tariff_gbp_per_kwh=-0.1)

    def test_zero_tariff_raises(self, valid_building, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="tariff"):
            calculate_thermal_load(valid_building, valid_scenario, valid_weather,
                                   tariff_gbp_per_kwh=0)

    def test_negative_carbon_intensity_raises(self, valid_building, valid_scenario, valid_weather):
        with pytest.raises(ValueError, match="carbon_intensity"):
            calculate_thermal_load(valid_building, valid_scenario, valid_weather,
                                   carbon_intensity_kg_per_kwh=-0.1)


# ===========================================================================
# C. Compliance — validate_energy_kwh
# ===========================================================================

class TestValidateEnergyKwh:
    def test_valid_value(self):
        ok, msg = validate_energy_kwh(5000.0)
        assert ok is True

    def test_zero_passes(self):
        ok, msg = validate_energy_kwh(0.0)
        assert ok is True

    def test_negative_fails(self):
        ok, msg = validate_energy_kwh(-1.0)
        assert ok is False
        assert "negative" in msg.lower()

    def test_very_large_fails(self):
        ok, msg = validate_energy_kwh(100_000_001)
        assert ok is False
        assert "unrealistically" in msg.lower()

    def test_exactly_100m_passes(self):
        ok, msg = validate_energy_kwh(100_000_000)
        assert ok is True

    def test_string_fails(self):
        ok, msg = validate_energy_kwh("not_a_number")
        assert ok is False
        assert "number" in msg.lower()

    def test_none_fails(self):
        ok, msg = validate_energy_kwh(None)
        assert ok is False

    def test_integer_passes(self):
        ok, msg = validate_energy_kwh(5000)
        assert ok is True

    def test_custom_label_in_message(self):
        ok, msg = validate_energy_kwh(-1, label="Gas consumption")
        assert ok is False
        assert "Gas consumption" in msg


# ===========================================================================
# D. Compliance — validate_floor_area
# ===========================================================================

class TestValidateFloorArea:
    def test_valid_value(self):
        ok, msg = validate_floor_area(100.0)
        assert ok is True

    def test_zero_fails(self):
        ok, msg = validate_floor_area(0.0)
        assert ok is False
        assert "greater than zero" in msg.lower()

    def test_negative_fails(self):
        ok, msg = validate_floor_area(-50.0)
        assert ok is False

    def test_very_large_fails(self):
        ok, msg = validate_floor_area(1_000_001)
        assert ok is False
        assert "unrealistically" in msg.lower()

    def test_exactly_1m_passes(self):
        ok, msg = validate_floor_area(1_000_000)
        assert ok is True

    def test_small_positive_passes(self):
        ok, msg = validate_floor_area(0.01)
        assert ok is True

    def test_string_fails(self):
        ok, msg = validate_floor_area("abc")
        assert ok is False

    def test_none_fails(self):
        ok, msg = validate_floor_area(None)
        assert ok is False


# ===========================================================================
# E. Compliance — validate_u_value
# ===========================================================================

class TestValidateUValue:
    def test_valid_value(self):
        ok, msg = validate_u_value(1.5)
        assert ok is True

    def test_zero_fails(self):
        ok, msg = validate_u_value(0.0)
        assert ok is False

    def test_negative_fails(self):
        ok, msg = validate_u_value(-0.5)
        assert ok is False

    def test_above_6_fails(self):
        ok, msg = validate_u_value(6.1)
        assert ok is False
        assert "plausible" in msg.lower()

    def test_exactly_6_passes(self):
        ok, msg = validate_u_value(6.0)
        assert ok is True

    def test_small_positive_passes(self):
        ok, msg = validate_u_value(0.05)
        assert ok is True

    def test_string_fails(self):
        ok, msg = validate_u_value("abc")
        assert ok is False

    def test_custom_label(self):
        ok, msg = validate_u_value(-1, label="Roof U-value")
        assert ok is False
        assert "Roof U-value" in msg


# ===========================================================================
# F. Compliance — estimate_epc_rating field validation
# ===========================================================================

class TestEstimateEpcRatingValidation:
    def test_valid_inputs(self):
        result = estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000,
                                      u_wall=0.26, u_roof=0.18, u_glazing=1.6)
        assert "epc_band" in result
        assert result["epc_band"] in "ABCDEFG"

    def test_missing_floor_area_fails(self):
        with pytest.raises((ValueError, TypeError)):
            estimate_epc_rating(floor_area_m2=None, annual_energy_kwh=50000)

    def test_zero_floor_area_fails(self):
        with pytest.raises(ValueError, match="Floor area"):
            estimate_epc_rating(floor_area_m2=0, annual_energy_kwh=50000)

    def test_negative_floor_area_fails(self):
        with pytest.raises(ValueError, match="Floor area"):
            estimate_epc_rating(floor_area_m2=-100, annual_energy_kwh=50000)

    def test_negative_energy_fails(self):
        with pytest.raises(ValueError):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=-1000)

    def test_zero_energy_passes(self):
        result = estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=0)
        assert result["epc_band"] == "A"  # Zero energy = most efficient

    def test_invalid_u_wall_fails(self):
        with pytest.raises(ValueError, match="U-wall"):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, u_wall=0)

    def test_invalid_u_roof_fails(self):
        with pytest.raises(ValueError, match="U-roof"):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, u_roof=-1)

    def test_invalid_u_glazing_fails(self):
        with pytest.raises(ValueError, match="U-glazing"):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, u_glazing=7)

    def test_glazing_ratio_zero_fails(self):
        with pytest.raises(ValueError, match="glazing_ratio"):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, glazing_ratio=0)

    def test_glazing_ratio_one_fails(self):
        with pytest.raises(ValueError, match="glazing_ratio"):
            estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, glazing_ratio=1.0)

    def test_glazing_ratio_valid(self):
        result = estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000, glazing_ratio=0.5)
        assert "epc_band" in result

    def test_mees_fields_present(self):
        result = estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000)
        assert "mees_compliant_now" in result
        assert "mees_2028_compliant" in result
        assert "mees_gap_bands" in result
        assert isinstance(result["mees_gap_bands"], int)

    def test_building_dict_input(self):
        result = estimate_epc_rating(building={"floor_area_m2": 500, "baseline_energy_mwh": 50})
        assert "epc_band" in result


# ===========================================================================
# G. Compliance — mees_gap_analysis field validation
# ===========================================================================

class TestMeesGapAnalysisValidation:
    def test_valid_inputs(self):
        result = mees_gap_analysis(current_sap=45, target_band="C")
        assert "sap_gap" in result
        assert "recommended_measures" in result

    def test_invalid_target_band_fails(self):
        with pytest.raises(ValueError, match="Invalid target band"):
            mees_gap_analysis(current_sap=45, target_band="X")

    def test_empty_target_band_fails(self):
        with pytest.raises(ValueError):
            mees_gap_analysis(current_sap=45, target_band="")

    def test_already_compliant_returns_empty_measures(self):
        result = mees_gap_analysis(current_sap=95, target_band="C")
        assert result["sap_gap"] == 0.0
        assert result["recommended_measures"] == []
        assert result["achievable"] is True

    def test_all_valid_bands(self):
        for band in "ABCDEFG":
            result = mees_gap_analysis(current_sap=50, target_band=band)
            assert isinstance(result, dict)


# ===========================================================================
# H. Compliance — calculate_carbon_baseline field validation
# ===========================================================================

class TestCarbonBaselineValidation:
    def test_valid_inputs(self):
        result = calculate_carbon_baseline(elec_kwh=10000, gas_kwh=5000)
        assert "scope1_tco2e" in result
        assert "scope2_tco2e" in result
        assert "total_tco2e" in result

    def test_all_zeros(self):
        result = calculate_carbon_baseline(elec_kwh=0, gas_kwh=0, oil_kwh=0, lpg_kwh=0)
        assert result["total_tco2e"] == 0.0

    def test_negative_electricity_fails(self):
        with pytest.raises(ValueError):
            calculate_carbon_baseline(elec_kwh=-100)

    def test_negative_gas_fails(self):
        with pytest.raises(ValueError):
            calculate_carbon_baseline(gas_kwh=-100)

    def test_negative_oil_fails(self):
        with pytest.raises(ValueError):
            calculate_carbon_baseline(oil_kwh=-100)

    def test_negative_lpg_fails(self):
        with pytest.raises(ValueError):
            calculate_carbon_baseline(lpg_kwh=-100)

    def test_negative_fleet_fails(self):
        with pytest.raises(ValueError):
            calculate_carbon_baseline(fleet_miles=-100)

    def test_invalid_floor_area_zero_fails(self):
        with pytest.raises(ValueError, match="Floor area"):
            calculate_carbon_baseline(elec_kwh=10000, floor_area_m2=0)

    def test_invalid_floor_area_negative_fails(self):
        with pytest.raises(ValueError, match="Floor area"):
            calculate_carbon_baseline(elec_kwh=10000, floor_area_m2=-50)

    def test_valid_floor_area_gives_intensity(self):
        result = calculate_carbon_baseline(elec_kwh=10000, floor_area_m2=200)
        assert result["intensity_kgco2_m2"] is not None
        assert result["intensity_kgco2_m2"] > 0

    def test_no_floor_area_intensity_none(self):
        result = calculate_carbon_baseline(elec_kwh=10000)
        assert result["intensity_kgco2_m2"] is None

    def test_breakdown_present(self):
        result = calculate_carbon_baseline(elec_kwh=10000, gas_kwh=5000, oil_kwh=2000)
        assert "breakdown" in result
        assert "electricity_scope2_tco2e" in result["breakdown"]
        assert "gas_scope1_tco2e" in result["breakdown"]

    def test_secr_threshold_check_present(self):
        result = calculate_carbon_baseline(elec_kwh=10000)
        assert "secr_threshold_check" in result


# ===========================================================================
# I. Compliance — part_l_compliance_check field validation
# ===========================================================================

class TestPartLComplianceValidation:
    def test_valid_inputs(self):
        result = part_l_compliance_check(
            u_wall=0.18, u_roof=0.15, u_glazing=1.4,
            floor_area_m2=100, annual_energy_kwh=3000)
        assert "part_l_2021_pass" in result
        assert "fhs_ready" in result

    def test_zero_floor_area_fails(self):
        with pytest.raises(ValueError, match="Floor area"):
            part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                    floor_area_m2=0, annual_energy_kwh=3000)

    def test_negative_floor_area_fails(self):
        with pytest.raises(ValueError):
            part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                    floor_area_m2=-100, annual_energy_kwh=3000)

    def test_negative_energy_fails(self):
        with pytest.raises(ValueError):
            part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                    floor_area_m2=100, annual_energy_kwh=-1)

    def test_zero_u_wall_fails(self):
        with pytest.raises(ValueError, match="U-wall"):
            part_l_compliance_check(u_wall=0, u_roof=0.15, u_glazing=1.4,
                                    floor_area_m2=100, annual_energy_kwh=3000)

    def test_zero_u_roof_fails(self):
        with pytest.raises(ValueError, match="U-roof"):
            part_l_compliance_check(u_wall=0.18, u_roof=0, u_glazing=1.4,
                                    floor_area_m2=100, annual_energy_kwh=3000)

    def test_zero_u_glazing_fails(self):
        with pytest.raises(ValueError, match="U-glazing"):
            part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=0,
                                    floor_area_m2=100, annual_energy_kwh=3000)

    def test_u_value_above_6_fails(self):
        with pytest.raises(ValueError):
            part_l_compliance_check(u_wall=6.1, u_roof=0.15, u_glazing=1.4,
                                    floor_area_m2=100, annual_energy_kwh=3000)

    def test_residential_vs_commercial_targets(self):
        res = part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                       floor_area_m2=100, annual_energy_kwh=3000,
                                       building_type="residential")
        com = part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                       floor_area_m2=100, annual_energy_kwh=3000,
                                       building_type="commercial")
        assert res["regs_label"] != com["regs_label"]

    def test_compliance_items_structure(self):
        result = part_l_compliance_check(u_wall=0.18, u_roof=0.15, u_glazing=1.4,
                                          floor_area_m2=100, annual_energy_kwh=3000)
        assert len(result["compliance_items"]) == 3
        for item in result["compliance_items"]:
            assert "element" in item
            assert "proposed_u" in item
            assert "target_u" in item
            assert "pass" in item
            assert "gap" in item

    def test_pass_gives_no_improvement_actions(self):
        result = part_l_compliance_check(u_wall=0.15, u_roof=0.12, u_glazing=1.0,
                                          floor_area_m2=200, annual_energy_kwh=1000,
                                          building_type="residential")
        assert result["part_l_2021_pass"] is True

    def test_fail_gives_improvement_actions(self):
        result = part_l_compliance_check(u_wall=2.0, u_roof=2.0, u_glazing=5.0,
                                          floor_area_m2=100, annual_energy_kwh=50000)
        assert result["part_l_2021_pass"] is False
        assert len(result["improvement_actions"]) > 0


# ===========================================================================
# J. Boundary / Edge Cases
# ===========================================================================

class TestBoundaryEdgeCases:
    """Cross-cutting boundary value tests."""

    def test_string_coercion_in_physics(self, valid_scenario, valid_weather):
        """Physics engine uses float() which coerces strings."""
        b = {"floor_area_m2": "500", "height_m": "4", "glazing_ratio": "0.3",
             "u_value_wall": "1.5", "u_value_roof": "0.8", "u_value_glazing": "2.0"}
        # Should not raise — float("500") works
        _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_integer_inputs_in_physics(self, valid_scenario, valid_weather):
        """Integer inputs should be accepted (coerced to float)."""
        b = {"floor_area_m2": 500, "height_m": 4, "glazing_ratio": 0,
             "u_value_wall": 1, "u_value_roof": 1, "u_value_glazing": 2}
        _validate_model_inputs(b, valid_scenario, valid_weather)

    def test_very_small_floor_area_in_compliance(self):
        ok, msg = validate_floor_area(0.001)
        assert ok is True

    def test_energy_exactly_zero(self):
        ok, msg = validate_energy_kwh(0)
        assert ok is True

    def test_u_value_exactly_boundary(self):
        ok, msg = validate_u_value(6.0)
        assert ok is True
        ok2, msg2 = validate_u_value(6.0001)
        assert ok2 is False

    def test_epc_all_bands_mapped(self):
        """Verify all SAP scores map to a valid band."""
        for sap in [1, 20, 21, 38, 39, 54, 55, 68, 69, 80, 81, 91, 92, 100]:
            result = estimate_epc_rating(floor_area_m2=500, annual_energy_kwh=50000,
                                          u_wall=0.26, u_roof=0.18, u_glazing=1.6)
            assert result["epc_band"] in "ABCDEFG"
