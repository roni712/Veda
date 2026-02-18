# demo_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, Connection, Dataset, SchemaSnapshot, Incident
from models.incident import Incident
from models.schema_snapshot import SchemaSnapshot
from models.models import Dataset
from models.connection import Connection 
from models.models import Base

import os

# -------------------------------
# 1️⃣ Database connection
# -------------------------------
DB_USER = os.getenv("POSTGRES_USER", "veda_admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "veda_beta123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "veda_meta")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# -------------------------------
# 2️⃣ Drop & recreate tables
# -------------------------------
print("Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)
print("Creating tables from models...")
Base.metadata.create_all(bind=engine)

# -------------------------------
# 3️⃣ Insert demo data
# -------------------------------
db = SessionLocal()

# Add a demo connection
conn = Connection(
    name="demo_connection",
    host="localhost",
    port=5432,
    database="veda",
    username="postgres",
    password="password"
)
db.add(conn)
db.commit()
db.refresh(conn)

# Add a demo dataset
dataset = Dataset(
    connection_id=conn.id,
    name="demo_dataset"
)
db.add(dataset)
db.commit()
db.refresh(dataset)

# Add a demo schema snapshot
snapshot = SchemaSnapshot(
    dataset_id=dataset.id,
    dataset_name=dataset.name,
    schema_json={
        "schema": "ops",
        "table": "pipeline_runs",
        "columns": [
            {"name": "run_id", "type": "integer", "nullable": "NO"},
            {"name": "pipeline_name", "type": "text", "nullable": "NO"},
            {"name": "status", "type": "text", "nullable": "NO"},
            {"name": "started_at", "type": "timestamp without time zone", "nullable": "NO"},
            {"name": "finished_at", "type": "timestamp without time zone", "nullable": "YES"}
        ]
    }
)
db.add(snapshot)
db.commit()
db.refresh(snapshot)

# Add a demo incident
incident = Incident(
    connection_id=conn.id,
    dataset_name=dataset.name,
    rule_type="SCHEMA_DRIFT",
    severity="LOW",
    details={"info": "demo incident"},
    status="open"
)
db.add(incident)
db.commit()
db.refresh(incident)

print("✅ Demo database setup complete!")
print(f"Connection ID: {conn.id}, Dataset ID: {dataset.id}, Snapshot ID: {snapshot.id}, Incident ID: {incident.id}")

db.close()
