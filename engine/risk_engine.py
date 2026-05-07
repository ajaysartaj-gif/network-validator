# -------------------------------
# ADVANCED RISK ENGINE
# -------------------------------

def advanced_risk_reasoning(
        semantic_objects):

    score = 0
    reasons = []
    recommendations = []

    for obj in semantic_objects:

        feature = obj.get("feature")
        risk = obj.get("risk")
        role = obj.get("device_role")

        # -------------------------------
        # BASE RISK
        # -------------------------------

        if risk == "HIGH":
            score += 25

        elif risk == "MEDIUM":
            score += 10

        else:
            score += 3

        # -------------------------------
        # ROLE MULTIPLIER
        # -------------------------------

        if role == "core_router":

            score += 20

            reasons.append(
                f"{feature} impacts core routing"
            )

        elif role == "firewall":

            score += 15

            reasons.append(
                f"{feature} impacts security perimeter"
            )

        elif role == "distribution_switch":

            score += 10

            reasons.append(
                f"{feature} impacts distribution layer"
            )

        # -------------------------------
        # FEATURE RISK
        # -------------------------------

        if feature in [
            "ospf",
            "bgp",
            "stp",
            "acl",
            "aaa"
        ]:

            score += 15

            reasons.append(
                f"Critical feature detected: {feature}"
            )

        # -------------------------------
        # SECURITY RISK
        # -------------------------------

        if feature == "telnet":

            score += 30

            reasons.append(
                "Insecure management protocol detected"
            )

            recommendations.append(
                "Replace Telnet with SSH"
            )

    # -------------------------------
    # LIMIT SCORE
    # -------------------------------

    score = min(score, 100)

    # -------------------------------
    # FINAL LEVEL
    # -------------------------------

    if score >= 80:
        level = "CRITICAL"

    elif score >= 50:
        level = "HIGH"

    elif score >= 25:
        level = "MEDIUM"

    else:
        level = "LOW"

    # -------------------------------
    # OUTPUT
    # -------------------------------

    return {

        "advanced_risk_score": score,

        "advanced_risk_level": level,

        "reasons": reasons,

        "recommendations": recommendations
    }
