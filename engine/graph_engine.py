# -------------------------------
# RELATIONSHIP GRAPH ENGINE
# -------------------------------

def build_relationship_graph(semantic_objects):

    relationships = []

    for obj in semantic_objects:

        feature = obj.get("feature")
        dependencies = obj.get("dependencies", [])

        for dep in dependencies:

            relationships.append({

                "source": feature,

                "target": dep,

                "relationship": "depends_on",

                "device_role":
                    obj.get("device_role", "unknown"),

                "domain":
                    obj.get("domain", "unknown")
            })

    return relationships
