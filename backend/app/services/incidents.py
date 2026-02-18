from app.models.incident import Incident

def get_open_incident(db, dataset_id, incident_type):
    return db.query(Incident).filter(
        Incident.dataset_id == dataset_id,
        Incident.type == incident_type,
        Incident.status == "open"
    ).first()
