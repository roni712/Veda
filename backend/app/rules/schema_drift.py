def detect_schema_drift(old_schema: dict, new_schema: dict):
    old_cols = {c["name"]: c for c in old_schema["columns"]}
    new_cols = {c["name"]: c for c in new_schema["columns"]}

    added = list(set(new_cols) - set(old_cols))
    removed = list(set(old_cols) - set(new_cols))

    type_changed = []
    for col in old_cols:
        if col in new_cols:
            if old_cols[col]["type"] != new_cols[col]["type"]:
                type_changed.append(col)

    return {
        "added_columns": added,
        "removed_columns": removed,
        "type_changed": type_changed
    }
