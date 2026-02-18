from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from app.models.models import Base

class Connection(Base):
    """
    Represents a database connection configuration.

    Attributes:
        id (int): Unique identifier for the connection.
        name (str): Display name for the connection.
        host (str): Database host address.
        port (int): Database port (default 5432).
        database (str): Database name.
        username (str): Database username.
        password (str): Database password (stored as plain text currently, should be encrypted).
        created_at (datetime): Timestamp when the connection was created.
    """
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), index=True)

    host: Mapped[str] = mapped_column(String(255))
    
    port: Mapped[int] = mapped_column(Integer, default=5432)
    
    database: Mapped[str] = mapped_column(String(255))
    
    username: Mapped[str] = mapped_column(String(255))
    
    password: Mapped[str] = mapped_column(String(255))  # later we encrypt

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
