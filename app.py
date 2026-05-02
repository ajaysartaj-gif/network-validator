import streamlit as st

# -------------------------------
# FILE READER
# -------------------------------
def read_file(file):
    try:
        return file.read().decode("utf-8")
    except:
        return str(file.read())


# -------------------------------
# PARSER
# -------------------------------
def parse_config(config):
    if not config or len(config.strip()) == 0:
        return {
            "hostname": None,
            "vlans": [],
            "interfaces": [],
            "acls": [],
            "routing": []
        }

    lines = config.splitlines()

    hostname = None
    vlans = set()
    interfaces = set()
    acls = set()
    routing = set()

    for raw_line in lines:
        line = raw_line.strip().lower()

        # Skip empty or comments
        if not line or line.startswith(("!", "#", "//")):
            continue

        # HOSTNAME
        if line.startswith("hostname "):
            parts = line.split()
            if len(parts) >= 2:
                hostname = parts[1]

        # VLAN
        elif line.startswith("vlan "):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                vlans.add(parts[1])

        # INTERFACE
        elif line.startswith("interface "):
            parts = line.split()
            if len(parts) >= 2:
                interfaces.add(parts[1])

        # ACL
        elif line.startswith("access-list"):
            acls.add(line)

        # ROUTING
        elif line.startswith("router ospf") or line.startswith("router bgp"):
            routing.add(line)

    return {
        "hostname": hostname,
        "vlans": sorted(list(vlans)),
        "interfaces": sorted(list(interfaces)),
        "acls": sorted(list(acls)),
        "routing": sorted(list(routing))
    }
# -------------------------------
# COMPARE
# -------------------------------
def compare_configs(c1, c2):
    changes = []

    changes += [f"VLAN {v} removed" for v in set(c1["vlans"]) - set(c2["vlans"])]
    changes += [f"VLAN {v} added" for v in set(c2["vlans"]) - set(c1["vlans"])]

    changes += [f"Interface {i} removed" for i in set(c1["interfaces"]) - set(c2["interfaces"])]
    changes += [f"Interface {i} added" for i in set(c2["interfaces"]) - set(c1["interfaces"])]

    changes += [f"ACL removed: {a}" for a in set(c1["acls"]) - set(c2["acls"])]
    changes += [f"ACL added: {a}" for a in set(c2["acls"]) - set(c1["acls"])]

    changes += [f"Routing removed: {r}" for r in set(c1["routing"]) - set(c2["routing"])]
    changes += [f"Routing added: {r}" for r in set(c2["routing"]) - set(c1["routing"])]

    return changes


# -------------------------------
# IMPACT ANALYSIS
# -------------------------------
def impact_analysis(changes):
    results = []

    for change in changes:

        if "Routing removed" in change:
            risk = "HIGH"
            impact = "Routing removed → Core network connectivity may break"

        elif "ACL removed" in change:
            risk = "HIGH"
            impact = "Security policy removed → Traffic may be unrestricted"

        elif "Interface removed" in change:
            risk = "MEDIUM"
            impact = "Device connected may lose connectivity"

        elif "VLAN removed" in change:
            risk = "HIGH"
            impact = "Users in VLAN may lose access"

        elif "Routing added" in change:
            risk = "MEDIUM"
            impact = "New routing introduced → Verify neighbors and redistribution"

        elif "ACL added" in change:
            risk = "MEDIUM"
            impact = "New security rule applied → Verify traffic impact"

        elif "Interface added" in change:
            risk = "LOW"
            impact = "New interface added → Check configuration"

        elif "VLAN added" in change:
            risk = "LOW"
            impact = "New VLAN created → Ensure routing setup"

        else:
            risk = "LOW"
            impact = "Minor change detected"

        results.append({
            "change": change,
            "impact": impact,
            "risk": risk
        })

    return results


# -------------------------------
# RISK SCORE
# -------------------------------
def calculate_risk_score(analysis):
    score = 0

    for item in analysis:
        if "Routing" in item["change"]:
            score += 5
        elif "ACL" in item["change"]:
            score += 4
        elif "Interface" in item["change"]:
            score += 2
        elif "VLAN" in item["change"]:
            score += 3

    return score


# -------------------------------
# FINAL DECISION
# -------------------------------
def final_decision(analysis):
    score = calculate_risk_score(analysis)

    if score >= 5:
        return "❌ DO NOT APPLY (CRITICAL RISK)"
    elif score >= 3:
        return "⚠️ REVIEW REQUIRED"
    else:
        return "✅ SAFE TO APPLY"


# -------------------------------
# UI
# -------------------------------
st.title("🚀 Network Pre-Change Validator")

config_a_file = st.file_uploader("Upload Current Config")
config_b_file = st.file_uploader("Upload Proposed Config")

if st.button("Analyze"):

    if config_a_file is None or config_b_file is None:
        st.error("Please upload both config files")

    else:
       st.write("RAW CONFIG A:", config_a[:3000])
       st.write("RAW CONFIG B:", config_b[:3000])

       parsed_a = parse_config(config_a)
       parsed_b = parse_config(config_b)

       # 🔍 Controlled debug (only for you)
       with st.expander("DEBUG (Parser Output)"):
       st.json({"CONFIG_A": parsed_a, "CONFIG_B": parsed_b})

# 🚨 Validation
if not parsed_a and not parsed_b:
    st.error("Parsing failed: Empty or invalid config files")
    st.stop()

        changes = compare_configs(parsed_a, parsed_b)
        analysis = impact_analysis(changes)
        decision = final_decision(analysis)

        st.subheader("🔍 Changes Detected")
        if not changes:
            st.write("No changes detected")
        else:
            for c in changes:
                st.write("-", c)

        st.subheader("📊 Impact Analysis")
        for a in analysis:
            st.write(f"{a['change']} → {a['impact']} (Risk: {a['risk']})")

        st.subheader("🚨 Final Decision")
        st.write(decision)
