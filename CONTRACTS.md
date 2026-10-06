# Tool contracts

The model may call these. It may not recompute them in prose and then ignore the result.

## stay_time

Inputs: dose_rate_mR_per_h (required, number > 0), limit_mR (required, number > 0).
Output: hours = limit / dose_rate. Also return minutes.
Refuse if either input is missing or the user gives only "it's high."

This is arithmetic, not a protection recommendation. Say the limit was supplied by the user.

## decay

Inputs: rate_now, elapsed_hours, half_life_hours. All required.
Output: rate_now * 0.5 ** (elapsed_hours / half_life_hours).
Iodine-131 half-life is 8.02 days (192.5 h). Cesium-137 is 30.1 years. If the isotope is unnamed, refuse. Do not apply a single half-life to mixed fallout.

## bleach_dose

Inputs: gallons (required), concentration_percent (required), cloudy (bool).
Use PINNED_TABLES.md. Unknown concentration -> refuse.
Output the drops or mL and the 30-minute wait. Double if cloudy.

## seven_ten

Inputs: dose_rate_at_h1, hours_since_burst. Both required. Source must be a detonation, not a reactor leak.
Approximation only: factor = 10 ** (log10(hours_since_burst) / log10(7)).
rate = dose_rate_at_h1 / factor.
Always label the result approximate.
