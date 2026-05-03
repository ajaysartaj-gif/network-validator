import streamlit as st
import json
import os
import pandas as pd

# -------------------------------
# HISTORY (AI MEMORY)
# -------------------------------
HISTORY_FILE = "change_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

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
        line = line.strip().lower()

        if not line or line.startswith(("!", "#")):
            continue

        if line.startswith("hostname"):
            data["hostname"] = line.split()[1]

        elif line.startswith("vlan"):
            data["vlans"].add(line.split()[1])

        elif line.startswith("interface"):
            data["interfaces"].add(line.split()[1])

        elif line.startswith("access-list"):
            data["acls"].add(line)

        elif line.startswith("router ospf") or line.startswith("router bgp"):
            data["routing"].add(line)

        elif "set interfaces" in line:
            data["interfaces"].add(line.split()[2])

        elif "set vlans" in line and "vlan-id" in line:
            data["vlans"].add(line.split()[-1])

        elif "set protocols ospf" in line or "set protocols bgp" in line:
            data["routing"].add(line)

    return data

# -------------------------------
# COMPARE CONFIGS
# -------------------------------
def compare_configs(c1, c2):
    changes = []

    for v in c1["vlans"]:
        if v not in c2["vlans"]:
            changes.append(f"VLAN {v} removed")
    for v in c2["vlans"]:
        if v not in c1["vlans"]:
            changes.append(f"VLAN {v} added")

    for i in c1["interfaces"]:
        if i not in c2["interfaces"]:
            changes.append(f"Interface {i} removed")
    for i in c2["interfaces"]:
        if i not in c1["interfaces"]:
            changes.append(f"Interface {i} added")

    for a in c1["acls"]:
        if a not in c2["acls"]:
            changes.append(f"ACL removed: {a}")
    for a in c2["acls"]:
        if a not in c1["acls"]:
            changes.append(f"ACL added: {a}")

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
    history = load_history()

    for change in changes:
        c = change.lower()

        if "routing" in c and "removed" in c:
            risk = "HIGH"
            impact = "Routing removed → network connectivity may break"

        elif "acl" in c and "removed" in c:
            risk = "HIGH"
            impact = "Security rule removed → traffic may be unrestricted"

        elif "interface" in c and "removed" in c:
            risk = "MEDIUM"
            impact = "Connected device may lose connectivity"

        elif "vlan" in c and "removed" in c:
            risk = "HIGH"
            impact = "Users in VLAN may lose access"

        elif "routing" in c and "added" in c:
            risk = "MEDIUM"
            impact = "New routing introduced → verify neighbors"

        elif "acl" in c and "added" in c:
            risk = "MEDIUM"
            impact = "New security rule applied"

        elif "interface" in c and "added" in c:
            risk = "LOW"
            impact = "New interface added"

        elif "vlan" in c and "added" in c:
            risk = "LOW"
            impact = "New VLAN created"

        else:
            risk = "LOW"
            impact = "Minor change"

        confidence = "LOW"
        for past in history:
            if past["change"].lower() == change.lower():
                confidence = "HIGH"
                break

        results.append({
            "change": change,
            "impact": impact,
            "risk": risk,
            "confidence": confidence
        })

    return results

# -------------------------------
# FINAL DECISION
# -------------------------------
def final_decision(analysis):
    if any(a["risk"] == "HIGH" for a in analysis):
        return "❌ DO NOT APPLY (CRITICAL RISK)"
    elif any(a["risk"] == "MEDIUM" for a in analysis):
        return "⚠️ REVIEW REQUIRED"
    else:
        return "✅ SAFE TO APPLY"

# -------------------------------
# UI
# -------------------------------
st.title("🚀 Network Pre-Change Validator")

col1, col2 = st.columns(2)

with col1:
    config_a_text = st.text_area("Current Config")

with col2:
    config_b_text = st.text_area("Proposed Config")

if st.button("Analyze"):

    parsed_a = parse_config(config_a_text)
    parsed_b = parse_config(config_b_text)

    changes = compare_configs(parsed_a, parsed_b)
    analysis = impact_analysis(changes)
    decision = final_decision(analysis)

    st.subheader("🔍 Changes")
    for c in changes:
        st.write("-", c)

    st.subheader("📊 Analysis")
    for a in analysis:
        st.write(f"{a['change']} → {a['impact']} ({a['risk']}, Confidence: {a['confidence']})")

    st.subheader("🚨 Decision")
    st.write(decision)

    # SAVE HISTORY
    history = load_history()
    for a in analysis:
        entry = {"change": a["change"], "risk": a["risk"]}
        if entry not in history:
            history.append(entry)
    save_history(history)
