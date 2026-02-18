def diff_schema(old: dict, new: dict) -> dict:
    """
    Compares two schema dictionaries and identifies differences (added, removed, or changed columns).

    Args:
        old (dict): The previous schema dictionary (column name -> type).
        new (dict): The current schema dictionary (column name -> type).

    Returns:
        dict: A dictionary containing lists of 'added', 'removed', and 'changed' column names.
    """
    old_cols = set(old.keys())
    new_cols = set(new.keys())

    # Identify columns that are present in new but not in old
    added = list(new_cols - old_cols)
    
    # Identify columns that were present in old but are missing in new
    removed = list(old_cols - new_cols)

    changed = []
    # Check for type changes in common columns
    for col in old_cols & new_cols:
        if old[col] != new[col]:
            changed.append(col)

    return {
        "added": added,
        "removed": removed,
        "changed": changed
    }
