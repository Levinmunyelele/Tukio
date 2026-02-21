from pydantic import BaseModel

# 1. Base Schema (Shared properties)
class UserBase(BaseModel):
    email: str

# 2. Create Schema (What we need to register)
class UserCreate(UserBase):
    password: str

# 3. Read Schema (What we return to the user - NO PASSWORD!)
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# --- Event Schemas ---

class EventBase(BaseModel):
    title: str
    description: str
    ticket_price: int  # In KES

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    organizer_id: int

    class Config:
        from_attributes = True