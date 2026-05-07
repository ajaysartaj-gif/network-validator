# -------------------------------
# BLAST RADIUS ENGINE
# -------------------------------

def calculate_blast_radius(
        semantic_objects):

    impacted = []

    for obj in semantic_objects:

        feature = obj.get("feature")

        # -------------------------------
        # ROUTING
        # -------------------------------

        if feature in [
            "ospf",
            "bgp"
        ]:

            impacted.append({

                "feature": feature,

                "impact":
                    "routing_neighbors",

                "severity":
                    "HIGH"
            })

        # -------------------------------
        # VLAN
        # -------------------------------

        elif feature == "vlan":

            impacted.append({

                "feature": feature,

                "impact":
                    "user_connectivity",

                "severity":
                    "HIGH"
            })

        # -------------------------------
        # STP
        # -------------------------------

        elif feature == "stp":

            impacted.append({

                "feature": feature,

                "impact":
                    "switching_stability",

                "severity":
                    "HIGH"
            })

        # -------------------------------
        # ACL
        # -------------------------------

        elif feature == "acl":

            impacted.append({

                "feature": feature,

                "impact":
                    "traffic_security",

                "severity":
                    "HIGH"
            })

        # -------------------------------
        # SNMP
        # -------------------------------

        elif feature == "snmp":

            impacted.append({

                "feature": feature,

                "impact":
                    "monitoring_visibility",

                "severity":
                    "MEDIUM"
            })

    return impacted
