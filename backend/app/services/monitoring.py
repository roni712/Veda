from sqlalchemy.orm import Session
from app.models import SchemaSnapshot, Incident
from app.rules.schema_drift import detect_schema_drift
from app.rules.freshness import is_stale

def run_checks_for_dataset(
    db: Session,
    connection_id: int,
    dataset_id: int
):
    """
    Runs monitoring checks (Schema Drift and Freshness) for a specific dataset.
    
    Args:
        db (Session): Database session.
        connection_id (int): ID of the connection the dataset belongs to.
        dataset_id (int): ID or Name of the dataset (Note: Type hint says int but usage suggests str might be passed).
    """
    snapshots = (
        db.query(SchemaSnapshot)
        .filter(SchemaSnapshot.dataset_id == dataset_id)
        .order_by(SchemaSnapshot.created_at.desc())
        .limit(2)
        .all()
    )

    if len(snapshots) < 2:
        return

    latest, previous = snapshots[0], snapshots[1]

    # ---- Schema Drift ----
    drift = detect_schema_drift(previous.schema_json, latest.schema_json)

    has_drift = (
        drift["added_columns"]
        or drift["removed_columns"]
        or drift["type_changed"]
    )

    existing = (
        db.query(Incident)
        .filter(
            Incident.connection_id == connection_id,
            # change it here so it resposne show name instead of id
            Incident.dataset_name == str(dataset_id),
            Incident.rule_type == "SCHEMA_DRIFT",
            Incident.status == "open",
        )
        .first()
    )

    if has_drift:
        if not existing:
            db.add(
                Incident(
                    connection_id=connection_id,
                    # change it here so it resposne show name instead of id
                    dataset_name=str(dataset_id),
                    rule_type="SCHEMA_DRIFT",
                    severity="HIGH",
                    details=drift,
                    status="open",
                )
            )
    else:
        if existing:
            existing.status = "resolved"
    

    # ---- Freshness ----
    if is_stale(latest.created_at):
        incident = Incident(
            connection_id=connection_id,
            dataset_name=str(dataset_id),
            rule_type="FRESHNESS",
            severity="MEDIUM",
            details={"message": "Dataset has not been updated recently"},
        )
        db.add(incident)
