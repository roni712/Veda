from sqlalchemy.orm import Session
from app.models import SchemaSnapshot, Incident
from app.rules.schema_drift import detect_schema_drift
from app.rules.freshness import is_stale

def run_checks_for_dataset(db: Session, connection_id: int, dataset_id: int):
    """
    Executes health checks for a dataset, including schema drift and freshness.

    Args:
        db (Session): Database session.
        connection_id (int): Connection ID.
        dataset_id (int): Dataset ID.
    """

    snapshots = (
        db.query(SchemaSnapshot)
        .filter(SchemaSnapshot.dataset_id == dataset_id)
        .order_by(SchemaSnapshot.created_at.desc())
        .limit(2)
        .all()
    )

    print("Snapshots found:", len(snapshots))

    if len(snapshots) < 2:
        return

    latest, previous = snapshots

    drift = detect_schema_drift(previous.schema_json, latest.schema_json)

    print("Drift:", drift)

    if drift["added_columns"] or drift["removed_columns"] or drift["type_changed"]:
        incident = Incident(
            connection_id=connection_id,
            dataset_name=latest.dataset_name,
            rule_type="SCHEMA_DRIFT",
            severity="HIGH",
            details=drift,
        )
        db.add(incident)

    if is_stale(latest.created_at):
        incident = Incident(
            connection_id=connection_id,
            dataset_name=latest.dataset_name,
            rule_type="FRESHNESS",
            severity="MEDIUM",
            details={"message": "Dataset stale"},
        )
        db.add(incident)

    db.commit()
