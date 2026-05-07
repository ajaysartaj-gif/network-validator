# -------------------------------
# ADVANCED RISK ENGINE
# -------------------------------

def advanced_risk_reasoning(semantic_objects):

    score = 0
    reasons = []

    for obj in semantic_objects:

        role = obj["device_role"]
        risk = obj["risk"]
        feature = obj["feature"]

        if risk == "HIGH":
            score += 25

        elif risk == "MEDIUM":
            score += 10

        else:
            score += 3

        if role == "core_router":
            score += 20
            reasons.append(
                f"{feature} affects core routing infrastructure"
            )

        elif role == "firewall":
            score += 15
            reasons.append(
                f"{feature} affects security perimeter"
            )

    score = min(score, 100)

    if score >= 80:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "advanced_risk_score": score,
        "advanced_risk_level": level,
        "reasons": reasons
    }

