from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func, JSON, ForeignKey
from app.models.models import Base

class SchemaSnapshot(Base):
    __tablename__ = "schema_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"),index=True)

    dataset_name: Mapped[str] = mapped_column(String(255),index=True)

    schema_json: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
