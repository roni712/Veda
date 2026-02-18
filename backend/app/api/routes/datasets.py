from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Dataset

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("")
def create_dataset(name: str):
    """
    Creates a new dataset manually.

    Args:
        name (str): The name of the dataset.

    Returns:
        dict: The ID and name of the created dataset.
    """
    db: Session = SessionLocal()
    ds = Dataset(name=name)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    db.close()
    return {"id": ds.id, "name": ds.name}

@router.get("")
def list_datasets():
    """
    Lists all available datasets in the system.

    Returns:
        list: A list of all datasets (ID and name).
    """
    db: Session = SessionLocal()
    rows = db.query(Dataset).all()
    db.close()
    return [{"id": r.id, "name": r.name} for r in rows]
