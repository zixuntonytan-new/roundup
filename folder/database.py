from app.models import SessionLocal, init_db


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def startup():
    init_db()
