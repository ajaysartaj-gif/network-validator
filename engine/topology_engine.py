# -------------------------------
# TOPOLOGY ENGINE
# -------------------------------

def build_topology_view(
        semantic_objects):

    topology = {

        "neighbors": [],
        "layer2": [],
        "routing": [],
        "security": []
    }

    for obj in semantic_objects:

        feature = obj.get("feature")
        domain = obj.get("domain")

        # -------------------------------
        # DISCOVERY
        # -------------------------------

        if feature in [
            "lldp",
            "cdp"
        ]:

            topology["neighbors"].append({

                "feature": feature,

                "type": "neighbor_discovery"
            })

        # -------------------------------
        # LAYER2
        # -------------------------------

        if domain == "layer2":

            topology["layer2"].append({

                "feature": feature
            })

        # -------------------------------
        # ROUTING
        # -------------------------------

        if domain == "routing":

            topology["routing"].append({

                "feature": feature
            })

        # -------------------------------
        # SECURITY
        # -------------------------------

        if domain == "security":

            topology["security"].append({

                "feature": feature
            })

    return topology
