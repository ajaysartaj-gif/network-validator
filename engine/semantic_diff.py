# -------------------------------
# SEMANTIC DIFF ENGINE
# -------------------------------

def semantic_diff(old_semantic,
                  new_semantic):

    changes = []

    old_set = set([
        (
            o["domain"],
            o["feature"]
        )

        for o in old_semantic
    ])

    new_set = set([
        (
            o["domain"],
            o["feature"]
        )

        for o in new_semantic
    ])

    # -------------------------------
    # REMOVED
    # -------------------------------

    for item in old_set:

        if item not in new_set:

            changes.append({

                "action": "removed",

                "domain": item[0],

                "feature": item[1]
            })

    # -------------------------------
    # ADDED
    # -------------------------------

    for item in new_set:

        if item not in old_set:

            changes.append({

                "action": "added",

                "domain": item[0],

                "feature": item[1]
            })

    return changes
