from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationship: One user can own many events
    events = relationship("Event", back_populates="organizer")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    ticket_price = Column(Integer)
    organizer_id = Column(Integer, ForeignKey("users.id"))

    # Relationship: An event belongs to one organizer
    organizer = relationship("User", back_populates="events")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, index=True)
    phone_number = Column(String)
    amount = Column(Integer)
    status = Column(String)  # e.g., "Completed", "Failed", "Cancelled"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_hash = Column(String, unique=True, index=True) # E.g., TUK-001
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="VALID") # Can be changed to "USED" at the gate

    # Relationships
    event = relationship("Event")
    owner = relationship("User")