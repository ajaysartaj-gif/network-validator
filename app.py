import json
import os
import streamlit as st
from openai import OpenAI
from engine.taxonomy import SEMANTIC_TAXONOMY

HISTORY_FILE = "change_history.json"

SEMANTIC_TAXONOMY = {

    "routing": {
        "ospf": [
            "router ospf",
            "set protocols ospf"
        ],
        "bgp": [
            "router bgp",
            "set protocols bgp"
        ]
    },

    "security": {
        "acl": [
            "access-list",
            "firewall filter"
        ],
        "aaa": [
            "aaa",
            "tacacs",
            "radius",
            "set system login"
        ],
        "ssh": [
            "transport input ssh",
            "set system services ssh"
        ],
        "telnet": [
            "transport input telnet",
            "set system services telnet"
        ]
    },

    "monitoring": {
        "snmp": [
            "snmp-server",
            "set snmp"
        ],
        "syslog": [
            "logging host",
            "set system syslog"
        ],
        "netflow": [
            "flow exporter",
            "ip flow",
            "netflow"
        ]
    },

    "layer2": {
        "vlan": [
            "vlan",
            "set vlans"
        ],
        "stp": [
            "spanning-tree",
            "rstp",
            "mstp"
        ],
        "lldp": [
            "lldp",
            "cdp"
        ]
    },

    "layer2_security": {
        "port_security": [
            "switchport port-security"
        ],
        "dhcp_snooping": [
            "ip dhcp snooping"
        ],
        "arp_inspection": [
            "ip arp inspection"
        ]
    },

    "interface": {
        "physical_interface": [
            "interface",
            "set interfaces"
        ],
        "port_channel": [
            "port-channel",
            "ae"
        ]
    },

    "services": {
        "ntp": [
            "ntp server",
            "set system ntp"
        ],
        "dhcp": [
            "ip dhcp",
            "system services dhcp"
        ],
        "dns": [
            "ip name-server",
            "system name-server"
        ]
    },

    "vpn": {
        "ipsec": [
            "crypto isakmp",
            "set security ipsec"
        ],
        "gre": [
            "interface tunnel",
            "gr-"
        ]
    },

    "qos": {
        "policy_map": [
            "policy-map",
            "class-map",
            "class-of-service"
        ]
    }
}


# -------------------------------
# DEVICE ROLE MODEL
# -------------------------------

DEVICE_ROLE_RULES = {

    "core_router": [
        "core",
        "border",
        "wan"
    ],

    "distribution_switch": [
        "dist",
        "distribution"
    ],

    "access_switch": [
        "access"
    ],

    "firewall": [
        "firewall",
        "paloalto",
        "fortigate"
    ]
}

# -------------------------------
# RELATIONSHIP GRAPH
# -------------------------------

def build_relationship_graph(semantic_objects):

    relationships = []

    for obj in semantic_objects:

        feature = obj["feature"]

        dependencies = obj["dependencies"]

        for dep in dependencies:

            relationships.append({

                "source": feature,

                "target": dep,

                "relationship": "depends_on",

                "device_role": obj["device_role"]
            })

    return relationships


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
# -------------------------------
# HISTORY (AI MEMORY)
# -------------------------------
def load_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


# -------------------------------
# FILE READER
# -------------------------------
def read_file(file):
    try:
        return file.read().decode("utf-8")
    except Exception:
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

        # CISCO
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

        # JUNIPER
        elif line.startswith("set system host-name"):
            parts = line.split()
            data["hostname"] = parts[-1]

        elif "set interfaces" in line:
            parts = line.split()
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
            if past.get("change", "").lower() == change.lower():
                confidence = "HIGH"
                break

        confidence_reason = (
            "Seen in historical changes before"
            if confidence == "HIGH"
            else "New/unseen change pattern"
        )

        results.append({
            "change": change,
            "impact": impact,
            "risk": risk,
            "confidence": confidence,
            "confidence_reason": confidence_reason
        })

    return results


# -------------------------------
# PATTERN AI (V1)
# -------------------------------
def extract_pattern_features(changes):
    features = {
        "total_changes": len(changes),
        "routing_removed": 0,
        "routing_added": 0,
        "acl_removed": 0,
        "acl_added": 0,
        "vlan_removed": 0,
        "vlan_added": 0,
        "interface_removed": 0,
        "interface_added": 0,
        "high_risk_signals": 0,
    }

    for c in changes:
        lc = c.lower()
        if "routing" in lc and "removed" in lc:
            features["routing_removed"] += 1
            features["high_risk_signals"] += 1
        if "routing" in lc and "added" in lc:
            features["routing_added"] += 1
        if "acl" in lc and "removed" in lc:
            features["acl_removed"] += 1
            features["high_risk_signals"] += 1
        if "acl" in lc and "added" in lc:
            features["acl_added"] += 1
        if "vlan" in lc and "removed" in lc:
            features["vlan_removed"] += 1
            features["high_risk_signals"] += 1
        if "vlan" in lc and "added" in lc:
            features["vlan_added"] += 1
        if "interface" in lc and "removed" in lc:
            features["interface_removed"] += 1
        if "interface" in lc and "added" in lc:
            features["interface_added"] += 1

    return features


def pattern_similarity_score(changes, history):
    if not history or not changes:
        return 0.0, 0

    change_set = set([c.lower() for c in changes])
    past_changes = [h.get("change", "").lower() for h in history if h.get("change")]

    matched = sum(1 for c in change_set if c in past_changes)
    score = matched / max(len(change_set), 1)
    return round(score, 2), matched


def pattern_risk_score(features, similarity_score):
    score = 0
    score += features["high_risk_signals"] * 20
    score += features["interface_removed"] * 8
    score += min(features["total_changes"], 10) * 3
    score += int(similarity_score * 20)
    return min(score, 100)


def pattern_summary(changes):
    history = load_history()
    features = extract_pattern_features(changes)
    sim_score, matched_count = pattern_similarity_score(changes, history)
    risk_score = pattern_risk_score(features, sim_score)

    if risk_score >= 75:
        level = "CRITICAL"
    elif risk_score >= 45:
        level = "ELEVATED"
    else:
        level = "MODERATE"

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "similarity_score": sim_score,
        "matched_history_changes": matched_count,
        "features": features
    }


# -------------------------------
# FINAL DECISION
# -------------------------------
def final_decision(analysis):
    has_high = any(item["risk"] == "HIGH" for item in analysis)
    has_medium = any(item["risk"] == "MEDIUM" for item in analysis)

    if has_high:
        return "❌ DO NOT APPLY (CRITICAL RISK)"
    elif has_medium:
        return "⚠️ REVIEW REQUIRED"
    else:
        return "✅ SAFE TO APPLY"


# -------------------------------
# FREE FALLBACK REVIEW
# -------------------------------
def generate_fallback_review(analysis, decision):
    if not analysis:
        return (
            "### AI Review (Fallback)\n"
            "- No config changes detected.\n"
            "- Recommendation: proceed with standard post-change verification."
        )

    high = [a for a in analysis if a["risk"] == "HIGH"]
    medium = [a for a in analysis if a["risk"] == "MEDIUM"]
    low = [a for a in analysis if a["risk"] == "LOW"]

    lines = [
        "### AI Review (Fallback Mode)",
        f"- HIGH risk changes: {len(high)}",
        f"- MEDIUM risk changes: {len(medium)}",
        f"- LOW risk changes: {len(low)}",
        f"- Final Decision: {decision}",
        "",
        "Top checks:",
        "- Verify VLAN gateway reachability and host connectivity.",
        "- Validate routing neighbors/routes and path changes.",
        "- Confirm ACL behavior against intended traffic.",
        "",
        "Rollback:",
        "- Keep previous config snapshot ready.",
        "- Revert high-risk removals first (routing/ACL/VLAN).",
        "- Re-run validation after rollback."
    ]
    return "\n".join(lines)


# -------------------------------
# AI REVIEW (OPENROUTER FREE)
# -------------------------------
def generate_ai_recommendation(analysis, decision, model="openrouter/free"):
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    base_url = st.secrets.get("OPENROUTER_BASE_URL") or os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"

    if not api_key:
        return "⚠️ OPENROUTER_API_KEY not found. Add it in Streamlit Secrets."

    summary_lines = [
        f"- {item['change']} | Risk={item['risk']} | Impact={item['impact']}"
        for item in analysis
    ] or ["- No config changes detected"]

    pattern = pattern_summary([item["change"] for item in analysis])

    prompt = (
        "You are a senior network change reviewer.\n"
        "Given these changes, provide:\n"
        "1) Short risk summary\n"
        "2) Top 3 verification checks/commands\n"
        "3) Rollback plan bullets\n"
        "Keep it concise and practical.\n\n"
        f"Tool decision: {decision}\n"
        f"Pattern risk score: {pattern['risk_score']} ({pattern['risk_level']})\n"
        f"Similarity score: {pattern['similarity_score']}\n"
        "Changes:\n" + "\n".join(summary_lines)
    )

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400
        )

        content = resp.choices[0].message.content if resp and resp.choices else None
        if content and str(content).strip():
            return content

        return generate_fallback_review(analysis, decision)

    except Exception as e:
        return (
            f"⚠️ Free model unavailable/rate-limited: {e}\n\n"
            + generate_fallback_review(analysis, decision)
        )

# -------------------------------
# SEMANTIC ENGINE
# -------------------------------

semantic_objects = semantic_normalize(
    config_b,
    parsed_b
)

relationship_graph = build_relationship_graph(
    semantic_objects
)

advanced_risk = advanced_risk_reasoning(
    semantic_objects
)

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

ai_model = st.text_input("AI model", value="openrouter/free")


def get_config(text, file):
    if text and text.strip():
        return text
    elif file is not None:
        return read_file(file)
    else:
        return ""


if st.button("Analyze"):
    pattern = pattern_summary(changes)
    config_a = get_config(config_a_text, config_a_file)
    config_b = get_config(config_b_text, config_b_file)

    if not config_a or not config_b:
        st.error("Provide both configs (paste or upload)")
    else:
        parsed_a = parse_config(config_a)
        parsed_b = parse_config(config_b)

        changes = compare_configs(parsed_a, parsed_b)
        changes = sorted(changes)
        analysis = impact_analysis(changes)
        decision = final_decision(analysis)
        pattern = pattern_summary(changes)

        st.subheader("🔍 Changes Detected")
        if not changes:
            st.write("No changes detected")
        else:
            changes_table = [{"Change": c} for c in changes]
            st.table(changes_table)

        st.divider()

        history = load_history()
        for a in analysis:
            entry = {"change": a["change"], "risk": a["risk"]}
            if entry not in history:
                history.append(entry)
        save_history(history)

        st.subheader("📊 Impact Analysis")
        impact_table = [
            {
                "Change": a["change"],
                "Impact": a["impact"],
                "Risk": a["risk"],
                "Confidence": a["confidence"],
                "Confidence Reason": a["confidence_reason"]
            }
            for a in analysis
        ]
        st.table(impact_table)

        st.divider()

        st.subheader("🧠 Pattern AI Risk Engine")
        st.table([{
            "Pattern Risk Score (0-100)": pattern["risk_score"],
            "Pattern Risk Level": pattern["risk_level"],
            "Similarity Score": pattern["similarity_score"],
            "Matched Historical Changes": pattern["matched_history_changes"]
        }])
        st.divider()
        st.subheader("🧠 Semantic Objects")
        st.table(semantic_objects)
        st.caption("Pattern features extracted from this change set")
        st.table([pattern["features"]])
        st.divider()
        st.subheader("🔗 Relationship Graph")
        st.table(relationship_graph)
        st.divider()
        st.subheader("🚨 Advanced Risk Reasoning")
        st.table([advanced_risk])

        st.divider()

        st.subheader("🚨 Final Decision")
        st.write(decision)

        st.divider()

        st.subheader("🤖 AI Change Review")
        ai_text = generate_ai_recommendation(analysis, decision, ai_model)
        st.markdown(ai_text)
