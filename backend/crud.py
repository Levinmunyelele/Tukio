from sqlalchemy.orm import Session
import models
import schemas

# 1. Get user by email (To check if they already exist)
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# 2. Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    # In a real app, we would hash the password here!
    fake_hashed_password = user.password + "notreallyhashed"

    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 3. Create an Event
def create_event(db: Session, event: schemas.EventCreate, user_id: int):
    db_event = models.Event(**event.dict(), organizer_id=user_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# 4. Get all events
def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).offset(skip).limit(limit).all()