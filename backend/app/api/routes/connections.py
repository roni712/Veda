import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Connection, Dataset, SchemaSnapshot, Incident
from app.connectors.postgres_connector import discover_tables, get_table_schema
from app.services.monitoring import run_checks_for_dataset
from app.services.schema import get_latest_snapshot, save_snapshot
from app.services.schema_diff import diff_schema


router = APIRouter(prefix="/connections", tags=["connections"])

@router.post("")
def create_connection(
    name: str,
    host: str,
    port: int = 5432,
    database: str = "postgres",
    username: str = "postgres",
    password: str = "",
):
    """
    Creates a new database connection configuration.

    Args:
        name (str): The display name for the connection.
        host (str): The hostname or IP address of the database server.
        port (int): The port number (default: 5432).
        database (str): The name of the database to connect to.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        dict: The ID and name of the created connection.
    """
    db: Session = SessionLocal()

    conn = Connection(
        name=name,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
    )

    db.add(conn)
    db.commit()
    db.refresh(conn)
    db.close()

    return {"id": conn.id, "name": conn.name}


@router.post("/{connection_id}/discover")
def discover_connection_tables(connection_id: int):
    """
    Discovers tables in the connected database and checks for schema drift.

    This function performs the following steps:
    1. Retrieves connection details from the database.
    2. Connects to the external database and lists all available tables.
    3. For each table:
        a. Registers it as a Dataset if it doesn't exist.
        b. Fetches the current table schema (columns, types).
        c. Compares the current schema with the latest stored snapshot.
        d. Saves a new snapshot of the schema.
        e. Creates a Schema Drift Incident if changes are detected; otherwise, resolves existing drift incidents.

    Args:
        connection_id (int): The ID of the connection to discover.

    Returns:
        dict: Summary of tables found and new datasets created.

    Raises:
        HTTPException: If the connection is not found or discovery fails.
    """
    db: Session = SessionLocal()

    # 1. Retrieve connection details
    conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not conn:
        db.close()
        raise HTTPException(status_code=404, detail="Connection not found")

    try:
        # 2. Connect to external DB and list tables
        tables = discover_tables(
            host=conn.host,
            port=conn.port,
            database=conn.database,
            username=conn.username,
            password=conn.password,
        )
    except Exception as e:
        db.close()
        raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

    created = 0

    for full_name in tables:
        # 3a. Register Dataset if new
        dataset = (
            db.query(Dataset)
            .filter(Dataset.connection_id == conn.id)
            .filter(Dataset.name == full_name)
            .first()
        )

        if not dataset:
            dataset = Dataset(
                name=full_name,
                connection_id=conn.id
            )
            db.add(dataset)
            db.flush()  # get dataset.id
            created += 1

        schema, table = full_name.split(".", 1)

        # 3b. Fetch current table schema
        current_schema = get_table_schema(
            host=conn.host,
            port=conn.port,
            database=conn.database,
            username=conn.username,
            password=conn.password,
            schema=schema,
            table=table,
        )

        # 3c. Fetch latest snapshot for comparison
        latest_snapshot = get_latest_snapshot(db, dataset.id)

        if latest_snapshot:
            diff = diff_schema(
                latest_snapshot.schema_json,
                current_schema
            )
        else:
            diff = {"added": [], "removed": [], "changed": []}

        # 3d. Always save a NEW snapshot to track history
        save_snapshot(db, dataset.id, dataset.name, current_schema)

        # 3e. INCIDENT LOGIC (SCHEMA DRIFT)
        # Check if there is already an open incident for this dataset and rule type
        existing_incident = (
            db.query(Incident)
            .filter(
                Incident.dataset_name == dataset.name,
                Incident.rule_type == "SCHEMA_DRIFT",
                Incident.status == "open"
            )
            .first()
        )

        if diff["added"] or diff["removed"] or diff["changed"]:
            # Drift detected
            if not existing_incident:
                # Create a new incident if one doesn't already exist
                db.add(
                    Incident(
                        dataset_id=dataset.id,
                        dataset_name=dataset.name,
                        connection_id=conn.id,
                        rule_type="SCHEMA_DRIFT",
                        details=diff,
                        severity="HIGH",
                        status="open"
                    )
                )
        else:
            # No drift detected (schema matches latest snapshot)
            if existing_incident:
                # Resolve the existing incident
                existing_incident.status = "resolved"
                existing_incident.resolved_at = datetime.datetime.now(datetime.timezone.utc)


    db.commit()
    db.close()

    return {"tables_found": len(tables), "new_datasets_created": created}

# getting dataset for the connection id
@router.get("/{connection_id}/datasets")
def list_datasets_for_connection(connection_id: int):
    """
    Lists all datasets (tables) discovered for a specific connection.

    Args:
        connection_id (int): The ID of the connection.

    Returns:
        list: A list of datasets belonging to the connection.
    """
    db: Session = SessionLocal()
    rows = db.query(Dataset).filter(Dataset.connection_id == connection_id).all()
    db.close()
    return [{"id": r.id, "name": r.name, "connection_id": r.connection_id} for r in rows]


@router.post("/{connection_id}/run_checks")
def run_monitoring(connection_id: int):
    """
    Triggers monitoring checks for all datasets associated with a connection.

    Iterates through all datasets and runs configured checks (e.g., freshness, volume).

    Args:
        connection_id (int): The ID of the connection.

    Returns:
        dict: Status of the monitoring run.
    """
    db: Session = SessionLocal()

    datasets = (
        db.query(Dataset)
        .filter(Dataset.connection_id == connection_id)
        .all()
    )

    for ds in datasets:
        run_checks_for_dataset(db, connection_id, ds.name)

    db.commit()
    db.close()

    return {"status": "checks completed", "datasets_checked": len(datasets)}

@router.get("/{connection_id}/incidents")
def list_incidents(connection_id: int):
    """
    Lists all incidents (e.g., schema drift, freshness failures) for a connection.

    Args:
        connection_id (int): The ID of the connection.

    Returns:
        list: A list of incidents associated with the connection.
    """
    db: Session = SessionLocal()
    rows = db.query(Incident).filter(Incident.connection_id == connection_id).all()
    db.close()
    return rows
