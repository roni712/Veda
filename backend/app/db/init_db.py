from app.db.session import engine
from app.models import Base


def init():
    Base.metadata.create_all(bind=engine)
    print("✅ VEDA DB tables created")

if __name__ == "__main__":
    init()