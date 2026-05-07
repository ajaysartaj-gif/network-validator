

# -------------------------------
# SEMANTIC NORMALIZATION
# -------------------------------

def semantic_normalize(config, parsed_data):

    semantic_objects = []

    hostname = parsed_data.get("hostname")
    device_role = detect_device_role(hostname)

    for raw_line in config.splitlines():

        line = raw_line.strip().lower()

        if not line:
            continue

        for domain, features in SEMANTIC_TAXONOMY.items():

            for feature, patterns in features.items():

                for pattern in patterns:

                    if pattern in line:

                        semantic_objects.append({

                            "hostname": hostname,
                            "device_role": device_role,

                            "domain": domain,
                            "feature": feature,

                            "raw_config": raw_line,

                            "risk": semantic_default_risk(domain, feature),

                            "dependencies":
                                semantic_dependencies(feature),

                            "operational_impact":
                                semantic_operational_impact(feature)
                        })

    return semantic_objects
    
# -------------------------------
# DETECT DEVICE ROLE
# -------------------------------

def detect_device_role(hostname):

    if not hostname:
        return "unknown"

    h = hostname.lower()

    for role, keywords in DEVICE_ROLE_RULES.items():

        for keyword in keywords:

            if keyword in h:
                return role

    return "unknown"
# -------------------------------
# DEFAULT RISK ENGINE
# -------------------------------

def semantic_default_risk(domain, feature):

    HIGH = [
        "ospf",
        "bgp",
        "acl",
        "aaa",
        "telnet",
        "ipsec"
    ]

    MEDIUM = [
        "stp",
        "lldp",
        "netflow",
        "snmp",
        "policy_map"
    ]

    if feature in HIGH:
        return "HIGH"

    if feature in MEDIUM:
        return "MEDIUM"

    return "LOW"


# -------------------------------
# DEPENDENCY ENGINE
# -------------------------------

def semantic_dependencies(feature):

    dependency_map = {

        "ospf": [
            "interface",
            "ip_address"
        ],

        "bgp": [
            "interface",
            "routing"
        ],

        "vlan": [
            "interface",
            "stp"
        ],

        "stp": [
            "vlan",
            "interface"
        ],

        "snmp": [
            "monitoring"
        ],

        "policy_map": [
            "qos",
            "traffic"
        ]
    }

    return dependency_map.get(feature, [])





