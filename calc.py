"""Deterministic helpers. The model does not get a vote."""

from __future__ import annotations


def stay_time(dose_rate_mR_per_h: float, limit_mR: float) -> dict:
    if dose_rate_mR_per_h <= 0 or limit_mR <= 0:
        raise ValueError("dose rate and limit must be > 0")
    hours = limit_mR / dose_rate_mR_per_h
    return {"hours": hours, "minutes": hours * 60, "limit_source": "user"}


def decay(rate_now: float, elapsed_hours: float, half_life_hours: float) -> dict:
    if half_life_hours <= 0:
        raise ValueError("half-life must be > 0")
    return {"rate": rate_now * 0.5 ** (elapsed_hours / half_life_hours)}


def bleach_dose(gallons: float, concentration_percent: float, cloudy: bool) -> dict:
    if gallons <= 0:
        raise ValueError("gallons must be > 0")
    if not 5.0 <= concentration_percent <= 9.0:
        raise ValueError("pinned table covers 5% to 9% only; refuse otherwise")
    # CDC: 8 drops per gallon clear, 5-9% NaOCl. Double if cloudy.
    drops = 8 * gallons * (2 if cloudy else 1)
    ml = 0.5 * gallons * (2 if cloudy else 1)
    return {
        "drops": drops,
        "ml": ml,
        "wait_minutes": 30,
        "source": "CDC water-emergency, reviewed 2025-12-17",
    }


def seven_ten(dose_rate_at_h1: float, hours_since_burst: float) -> dict:
    if hours_since_burst <= 0:
        raise ValueError("hours must be > 0")
    import math
    factor = 10 ** (math.log10(hours_since_burst) / math.log10(7))
    return {
        "approx_dose_rate": dose_rate_at_h1 / factor,
        "label": "approximation for early fission-product fallout after a detonation, not a measurement",
    }


if __name__ == "__main__":
    assert bleach_dose(1, 6, False)["drops"] == 8
    assert bleach_dose(1, 6, True)["drops"] == 16
    assert abs(stay_time(100, 100)["hours"] - 1) < 1e-9
    print("ok")
