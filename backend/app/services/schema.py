from app.models.schema_snapshot import SchemaSnapshot


def save_snapshot(db, dataset_id: int, dataset_name: str, schema: dict):
    """
    Saves a new snapshot of a dataset's schema to the database.

    Args:
        db: The database session.
        dataset_id (int): The ID of the dataset.
        dataset_name (str): The name of the dataset.
        schema (dict): The JSON representation of the schema.
    
    Raises:
        TypeError: If dataset_id is not an integer.
    """
    if not isinstance(dataset_id, int):
        raise TypeError("dataset_id must be int")    
    snapshot = SchemaSnapshot(
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        schema_json=schema
    )
    db.add(snapshot)
    db.commit()

def get_latest_snapshot(db, dataset_id: int):
    """
    Retrieves the most recent schema snapshot for a given dataset.

    Args:
        db: The database session.
        dataset_id (int): The ID of the dataset.

    Returns:
        SchemaSnapshot: The latest snapshot object, or None if no snapshots exist.
    """
    return (
        db.query(SchemaSnapshot)
        .filter(SchemaSnapshot.dataset_id == dataset_id)
        .order_by(SchemaSnapshot.created_at.desc())
        .first()
    )
