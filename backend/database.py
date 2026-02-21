from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 1. Load the password from the .env file
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Create the "Engine" (The thing that actually talks to Postgres)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create a "Session" factory (Each request gets a new session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the "Base" class (All our models will inherit from this)
Base = declarative_base()

# 5. Dependency (We use this in main.py to get a database connection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()