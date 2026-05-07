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



