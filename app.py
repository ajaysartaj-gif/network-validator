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
    data = {
        "hostname": None,
        "vlans": set(),
        "interfaces": set(),
        "acls": set(),
        "routing": set()
    }

    for line in config.splitlines():
        raw = line.strip()
        line = raw.lower()

        if not line or line.startswith(("!", "#")):
            continue

        # -------------------------
        # CISCO
        # -------------------------
        if line.startswith("hostname"):
            parts = line.split()
            if len(parts) > 1:
                data["hostname"] = parts[1]

        elif line.startswith("vlan"):
            parts = line.split()
            if len(parts) > 1:
                data["vlans"].add(parts[1])

        elif line.startswith("interface"):
            parts = line.split()
            if len(parts) > 1:
                data["interfaces"].add(parts[1])

        elif line.startswith("access-list"):
            data["acls"].add(line)

        elif line.startswith("router ospf") or line.startswith("router bgp"):
            data["routing"].add(line)

        # -------------------------
        # JUNIPER
        # -------------------------
        elif line.startswith("set system host-name"):
            parts = line.split()
            data["hostname"] = parts[-1]

        elif "set interfaces" in line:
            parts = line.split()
            # Example: set interfaces ge-0/0/1 unit 0 ...
            if len(parts) > 2:
                data["interfaces"].add(parts[2])

        elif "set vlans" in line and "vlan-id" in line:
            parts = line.split()
            data["vlans"].add(parts[-1])

        elif "set protocols ospf" in line or "set protocols bgp" in line:
            data["routing"].add(line)

    return data

# -------------------------------
# COMPARE CONFIGS
# -------------------------------
def compare_configs(c1, c2):
    changes = []

    # VLAN
    for v in c1["vlans"]:
        if v not in c2["vlans"]:
            changes.append(f"VLAN {v} removed")
    for v in c2["vlans"]:
        if v not in c1["vlans"]:
            changes.append(f"VLAN {v} added")

    # INTERFACE
    for i in c1["interfaces"]:
        if i not in c2["interfaces"]:
            changes.append(f"Interface {i} removed")
    for i in c2["interfaces"]:
        if i not in c1["interfaces"]:
            changes.append(f"Interface {i} added")

    # ACL
    for a in c1["acls"]:
        if a not in c2["acls"]:
            changes.append(f"ACL removed: {a}")
    for a in c2["acls"]:
        if a not in c1["acls"]:
            changes.append(f"ACL added: {a}")

    # ROUTING
    for r in c1["routing"]:
        if r not in c2["routing"]:
            changes.append(f"Routing removed: {r}")
    for r in c2["routing"]:
        if r not in c1["routing"]:
            changes.append(f"Routing added: {r}")

    return changes


# -------------------------------
# IMPACT ANALYSIS
# -------------------------------
def impact_analysis(changes):
    results = []

    for change in changes:
        c = change.lower()   # ✅ normalize

        if "routing removed" in c:
            risk = "HIGH"
            impact = "Routing removed → network connectivity may break"

        elif "acl removed" in c:
            risk = "HIGH"
            impact = "Security rule removed → traffic may be unrestricted"

        elif "interface removed" in c:
            risk = "MEDIUM"
            impact = "Connected device may lose connectivity"

        elif "vlan removed" in c:
            risk = "HIGH"
            impact = "Users in VLAN may lose access"

        elif "routing added" in c:
            risk = "MEDIUM"
            impact = "New routing introduced → verify neighbors"

        elif "acl added" in c:
            risk = "MEDIUM"
            impact = "New security rule applied"

        elif "interface added" in c:
            risk = "LOW"
            impact = "New interface added"

        elif "vlan added" in c:
            risk = "LOW"
            impact = "New VLAN created"

        else:
            risk = "LOW"
            impact = "Minor change"

        results.append({
            "change": change,
            "impact": impact,
            "risk": risk
        }}
import pandas as pd

st.subheader("📋 Structured Output")

df = pd.DataFrame(analysis)
st.dataframe(df)

    return results
# -------------------------------
# RISK SCORE
# -------------------------------
def calculate_risk_score(analysis):
    score = 0

    for item in analysis:
        if "routing" in item["change"]:
            score += 5
        elif "acl" in item["change"]:
            score += 4
        elif "interface" in item["change"]:
            score += 2
        elif "vlan" in item["change"]:
            score += 3

    return score


# -------------------------------
# FINAL DECISION
# -------------------------------
def final_decision(analysis):

    has_high = False
    has_medium = False

    for item in analysis:
        if item["risk"] == "HIGH":
            has_high = True
        elif item["risk"] == "MEDIUM":
            has_medium = True

    if has_high:
        return "❌ DO NOT APPLY (CRITICAL RISK)"
    elif has_medium:
        return "⚠️ REVIEW REQUIRED"
    else:
        return "✅ SAFE TO APPLY"
# -------------------------------
# UI
# -------------------------------
st.title("🚀 Network Pre-Change Validator")

st.subheader("📥 Input Options")

col1, col2 = st.columns(2)

with col1:
    config_a_text = st.text_area("Paste Current Config (optional)", height=300)
    config_a_file = st.file_uploader("Or Upload Current Config")

with col2:
    config_b_text = st.text_area("Paste Proposed Config (optional)", height=300)
    config_b_file = st.file_uploader("Or Upload Proposed Config")

def get_config(text, file):
    # Priority: pasted text → file → empty
    if text and text.strip():
        return text
    elif file is not None:
        return read_file(file)
    else:
        return ""

if st.button("Analyze"):

    config_a = get_config(config_a_text, config_a_file)
    config_b = get_config(config_b_text, config_b_file)

    if not config_a or not config_b:
        st.error("Provide both configs (paste or upload)")
    else:
        parsed_a = parse_config(config_a)
        parsed_b = parse_config(config_b)

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

high = [a for a in analysis if a["risk"] == "HIGH"]
medium = [a for a in analysis if a["risk"] == "MEDIUM"]
low = [a for a in analysis if a["risk"] == "LOW"]

if high:
    st.error("🔴 HIGH RISK")
    for a in high:
        st.write(f"{a['change']} → {a['impact']}")

if medium:
    st.warning("🟡 MEDIUM RISK")
    for a in medium:
        st.write(f"{a['change']} → {a['impact']}")

if low:
    st.success("🟢 LOW RISK")
    for a in low:
        st.write(f"{a['change']} → {a['impact']}")
        import pandas as pd

st.subheader("📋 Structured Output")
df = pd.DataFrame(analysis)
st.dataframe(df)
