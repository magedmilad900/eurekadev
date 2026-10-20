"""Explainable scoring model for the GreenWatch educational prototype."""


def _clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def assess_water_quality(ph, turbidity, nitrate, dissolved_oxygen, temperature):
    score = 0
    reasons = []

    # The weights are intentionally transparent and documented in README.md.
    if ph < 6.5 or ph > 8.5:
        score += 25
        reasons.append(f"pH ({ph:.1f}) is outside the screening range of 6.5–8.5.")
    elif ph < 6.8 or ph > 8.2:
        score += 10
        reasons.append(f"pH ({ph:.1f}) is near the edge of the screening range.")
    else:
        reasons.append(f"pH ({ph:.1f}) is within the target screening range.")

    if turbidity > 10:
        score += 25
        reasons.append(f"Turbidity ({turbidity:.1f} NTU) is high and may indicate suspended particles.")
    elif turbidity > 5:
        score += 12
        reasons.append(f"Turbidity ({turbidity:.1f} NTU) is elevated.")
    else:
        reasons.append(f"Turbidity ({turbidity:.1f} NTU) is low in this screen.")

    if nitrate > 50:
        score += 25
        reasons.append(f"Nitrate ({nitrate:.1f} mg/L) is high in this screen.")
    elif nitrate > 10:
        score += 12
        reasons.append(f"Nitrate ({nitrate:.1f} mg/L) is elevated.")
    else:
        reasons.append(f"Nitrate ({nitrate:.1f} mg/L) is low in this screen.")

    if dissolved_oxygen < 3:
        score += 15
        reasons.append(f"Dissolved oxygen ({dissolved_oxygen:.1f} mg/L) is very low.")
    elif dissolved_oxygen < 5:
        score += 8
        reasons.append(f"Dissolved oxygen ({dissolved_oxygen:.1f} mg/L) is somewhat low.")
    else:
        reasons.append(f"Dissolved oxygen ({dissolved_oxygen:.1f} mg/L) is acceptable for this screen.")

    if temperature > 30 or temperature < 5:
        score += 10
        reasons.append(f"Temperature ({temperature:.1f}°C) is outside the prototype's typical range.")

    score = _clamp(score)
    if score < 25:
        risk = "Low"
        recommendations = [
            "Continue periodic monitoring using the same method.",
            "Record the date, location, weather, and measurements for comparison.",
        ]
    elif score < 55:
        risk = "Moderate"
        recommendations = [
            "Repeat the measurement to rule out a one-time reading error.",
            "Inspect the area for runoff, algae, waste, or recent heavy rain.",
            "Consider requesting a certified laboratory test.",
        ]
    else:
        risk = "High"
        recommendations = [
            "Do not make drinking-water decisions from this screen alone.",
            "Contact a local environmental or public-health authority.",
            "Arrange certified laboratory testing as soon as possible.",
        ]

    return {"score": score, "risk": risk, "reasons": reasons, "recommendations": recommendations}


def risk_color(risk):
    return {"Low": "#16803c", "Moderate": "#b26a00", "High": "#b42318"}[risk]
