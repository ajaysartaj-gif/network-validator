

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



