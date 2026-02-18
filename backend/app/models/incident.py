from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func, JSON, ForeignKey
from app.models.models import Base

class Incident(Base):
    """
    Represents a data quality incident detected in the system.

    Attributes:
        id (int): Unique identifier for the incident.
        connection_id (int): ID of the affected connection.
        dataset_name (str): Name of the affected dataset.
        rule_type (str): The type of rule that failed (e.g., 'SCHEMA_DRIFT', 'FRESHNESS').
        severity (str): Severity level of the incident ('LOW', 'MEDIUM', 'HIGH').
        details (dict): JSON details about the incident (e.g., schema diff).
        created_at (datetime): Timestamp when the incident was created.
        status (str): Current status of the incident ('open', 'resolved').
    """
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    connection_id: Mapped[int] = mapped_column(Integer, index=True)
    
    dataset_name: Mapped[str] = mapped_column(String(255), index=True)
    
    # dataset_id: Mapped[int] = mapped_column(Integer,index=True)
    
    rule_type: Mapped[str] = mapped_column(String(100))  # SCHEMA_DRIFT, FRESHNESS
   
    severity: Mapped[str] = mapped_column(String(50))    # LOW, MEDIUM, HIGH

    details: Mapped[dict] = mapped_column(JSON)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    status: Mapped[str] = mapped_column(String, default="open")  # open | resolved
    # started_at: Mapped[str]= mapped_column(DateTime(timezone=True), server_default=func.now())
    # resolved_at:Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)
