from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, ForeignKey

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models.
    """
    pass

class Dataset(Base):
    """
    Represents a dataset (table) discovered from a connection.

    Attributes:
        id (int): Unique identifier for the dataset.
        connection_id (int): Foreign key referencing the Connection this dataset belongs to.
        name (str): The full name of the dataset (e.g., 'schema.table').
        created_at (datetime): Timestamp when the dataset was first registered.
    """
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    connection_id: Mapped[int] = mapped_column(Integer, ForeignKey("connections.id"), index=True)
    
    name: Mapped[str] = mapped_column(String(255),index=True)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())