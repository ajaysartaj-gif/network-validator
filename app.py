import streamlit as st

# -------------------------------
# PARSER
# -------------------------------
def parse_config(config):
    lines = config.split("\n")
    hostname = None
    vlans = []
    interfaces = []
    acls = []
    routing = []

    for line in lines:
        line = line.strip()

        if line.startswith("hostname"):
            hostname = line.split()[1]

        if line.startswith("vlan"):
            parts = line.split()
            if len(parts) > 1:
                vlans.append(parts[1])

        if line.startswith("interface"):
            interfaces.append(line.split()[1])

        if line.startswith("access-list"):
            acls.append(line)

        if line.startswith("router ospf") or line.startswith("router bgp"):
            routing.append(line)

    return {
        "hostname": hostname,
        "vlans": vlans,
        "interfaces": interfaces,
        "acls": acls,
        "routing": routing
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
# IMPACT
# -------------------------------
def impact_analysis(changes):
    results = []

    for change in changes:

        if "Routing removed" in change:
            risk = "HIGH"
            impact = "Routes may not be advertised"

        elif "ACL removed" in change:
            risk = "HIGH"
            impact = "Security risk, traffic filtering removed"

        elif "Interface removed" in change:
            risk = "MEDIUM"
            impact = "Device may disconnect"

        elif "VLAN removed" in change:
            risk = "HIGH"
            impact = "Users may lose connectivity"

        else:
            risk = "LOW"
            impact = "Minor change"

        results.append({
            "change": change,
            "impact": impact,
            "risk": risk
        })

    return results


# -------------------------------
# DECISION
# -------------------------------
def final_decision(analysis):
    for item in analysis:
        if item["risk"] == "HIGH":
            return "❌ DO NOT APPLY"
    return "✅ SAFE TO APPLY"


# -------------------------------
# UI
# -------------------------------
st.title("🚀 Network Pre-Change Validator")

config_a = st.text_area("Paste Current Config")
config_b = st.text_area("Paste Proposed Config")

if st.button("Analyze"):

    parsed_a = parse_config(config_a)
    parsed_b = parse_config(config_b)

    changes = compare_configs(parsed_a, parsed_b)
    analysis = impact_analysis(changes)
    decision = final_decision(analysis)

    st.subheader("🔍 Changes Detected")
    for c in changes:
        st.write("-", c)

    st.subheader("📊 Impact Analysis")
    for a in analysis:
        st.write(f"{a['change']} → {a['impact']} (Risk: {a['risk']})")

    st.subheader("🚨 Final Decision")
    st.write(decision)
