from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine  
import models    
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
import schemas, crud
from database import get_db    
import mpesa
from pydantic import BaseModel 
from fastapi import Request

# This command tells SQLAlchemy: "Look at models.py and create 
# any tables that don't exist in the database yet."
models.Base.metadata.create_all(bind=engine)

class PaymentRequest(BaseModel):
    phone_number: str
    amount: int

# 1. Initialize the App
app = FastAPI(
    title="Tukio Event API",
    description="Backend for Tukio Ticketing System with M-Pesa Integration",
    version="1.0.0"
)

# 2. CORS (Security)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. The "Sanity Check" Route
@app.get("/")
def read_root():
    return {
        "status": "active",
        "message": "Welcome to Tukio API. Tables should be created now!",
        "docs": "/docs"
    }

# 4. M-Pesa Test Route (Placeholder)
@app.get("/api/v1/mpesa-status")
def check_mpesa():
    return {"status": "Waiting for credentials..."}

# 5. User Registration Route
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # A. Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # B. Create the user
    return crud.create_user(db=db, user=user)

# 6. Create an Event (Hardcoded user_id=1 for now)
@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    # In the future, we will get this ID from the logged-in token
    return crud.create_event(db=db, event=event, user_id=1)

# 7. List all Events
@app.get("/events/", response_model=list[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events

# 8. Trigger M-Pesa Payment
@app.post("/api/v1/pay")
def trigger_payment(payment: PaymentRequest):
    # Calls the engine we just built in mpesa.py
    result = mpesa.initiate_stk_push(payment.phone_number, payment.amount)
    return result

# 9. M-Pesa Callback Webhook
@app.post("/api/v1/callback")
async def mpesa_callback(payload: dict, db: Session = Depends(get_db)):
    print("----- M-PESA RECEIPT RECEIVED -----")
    
    # Safely navigate Safaricom's nested JSON
    body = payload.get("Body", {}).get("stkCallback", {})
    result_code = body.get("ResultCode")
    
    # ResultCode 0 means the user successfully entered their PIN and paid
    if result_code == 0:
        metadata = body.get("CallbackMetadata", {}).get("Item", [])
        
        # Helper function to extract specific fields from the metadata array
        def get_meta_value(key):
            for item in metadata:
                if item.get("Name") == key:
                    return item.get("Value")
            return None
            
        # Extract the exact details we need
        receipt = get_meta_value("MpesaReceiptNumber")
        phone = str(get_meta_value("PhoneNumber"))
        amount = int(get_meta_value("Amount"))
        
        # Save it directly into PostgreSQL
        new_transaction = models.Transaction(
            receipt_number=receipt,
            phone_number=phone,
            amount=amount,
            status="Completed"
        )
        db.add(new_transaction)
        db.commit()
        
        print(f"✅ SUCCESS: Saved Receipt {receipt} to Database!")
    else:
        # ResultCode != 0 means they cancelled or had insufficient funds
        error_desc = body.get("ResultDesc", "Unknown Error")
        print(f"❌ FAILED: Transaction failed - {error_desc}")
        
    return {"ResultCode": 0, "ResultDesc": "Accepted"}