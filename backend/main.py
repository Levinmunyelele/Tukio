from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel 
import uuid

# Project Imports
from database import engine, get_db  
import models    
import schemas, crud
import mpesa
import qr_service

# 1. Database Setup
# This command tells SQLAlchemy: "Look at models.py and create 
# any tables that don't exist in the database yet."
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the App
app = FastAPI(
    title="Tukio Event API",
    description="Backend for Tukio Ticketing System with M-Pesa Integration",
    version="1.0.0"
)

# 3. CORS (Security)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---
class PaymentRequest(BaseModel):
    phone_number: str
    amount: int

class TicketScan(BaseModel):
    ticket_hash: str

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        # Stores active connections. Key = Phone Number, Value = WebSocket
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_ticket(self, ticket_hash: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(ticket_hash)

manager = ConnectionManager()

# --- WebSocket Route ---
@app.websocket("/api/v1/ws/{phone_number}")
async def websocket_endpoint(websocket: WebSocket, phone_number: str):
    await manager.connect(websocket, phone_number)
    try:
        while True:
            # We just keep the connection open waiting for the backend to send something
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(phone_number)

# --- API Routes ---

@app.get("/")
def read_root():
    return {
        "status": "active",
        "message": "Welcome to Tukio API. System is operational.",
        "docs": "/docs"
    }

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event, user_id=1)

@app.get("/events/", response_model=list[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events

@app.post("/api/v1/pay")
def trigger_payment(payment: PaymentRequest):
    result = mpesa.initiate_stk_push(payment.phone_number, payment.amount)
    return result

# 9. M-Pesa Callback Webhook (Handles Transaction & Ticket Generation)
@app.post("/api/v1/callback")
async def mpesa_callback(payload: dict, db: Session = Depends(get_db)):
    print("----- M-PESA RECEIPT RECEIVED -----")
    
    body = payload.get("Body", {}).get("stkCallback", {})
    result_code = body.get("ResultCode")
    
    if result_code == 0:
        metadata = body.get("CallbackMetadata", {}).get("Item", [])
        
        def get_meta_value(key):
            for item in metadata:
                if item.get("Name") == key:
                    return item.get("Value")
            return None
            
        receipt = get_meta_value("MpesaReceiptNumber")
        phone = str(get_meta_value("PhoneNumber"))
        amount = int(get_meta_value("Amount"))
        
        # 1. Save the Transaction
        new_transaction = models.Transaction(
            receipt_number=receipt,
            phone_number=phone,
            amount=amount,
            status="Completed"
        )
        db.add(new_transaction)
        
        # 2. GENERATE THE TICKET
        unique_ticket_hash = f"TUK-{uuid.uuid4().hex[:8].upper()}"
        
        new_ticket = models.Ticket(
            ticket_hash=unique_ticket_hash,
            event_id=1,  # Hardcoded for test
            user_id=1,   # Hardcoded for test
            status="VALID"
        )
        db.add(new_ticket)
        db.commit() 
        
        # 3. Generate the actual QR Image file
        qr_service.generate_ticket_qr(unique_ticket_hash, phone)
        
        print(f"✅ SUCCESS: Transaction {receipt} saved.")
        print(f"🎟️ TICKET GENERATED: {unique_ticket_hash}")

        # 4. SEND TICKET TO FRONTEND VIA WEBSOCKET!
        await manager.send_ticket(unique_ticket_hash, phone)
        
    else:
        error_desc = body.get("ResultDesc", "Unknown Error")
        print(f"❌ FAILED: Transaction failed - {error_desc}")
        
    return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.get("/api/v1/ticket/{ticket_id}")
def get_ticket_qr(ticket_id: str, phone: str):
    file_path = qr_service.generate_ticket_qr(ticket_id, phone)
    return FileResponse(file_path)

# 11. Gatekeeper API - Scan Ticket at the Door
@app.post("/api/v1/scan")
def scan_ticket(scan_data: TicketScan, db: Session = Depends(get_db)):
    # 1. Look for the ticket in the database
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_hash == scan_data.ticket_hash).first()
    
    # 2. Does the ticket even exist?
    if not ticket:
        raise HTTPException(status_code=404, detail="FAKE TICKET: Not found in system!")
        
    # 3. Has it already been used?
    if ticket.status == "USED":
        raise HTTPException(status_code=400, detail="ENTRY DENIED: Ticket has already been scanned!")
        
    # 4. If it's VALID, let them in and mark as USED
    ticket.status = "USED"
    db.commit()
    db.refresh(ticket)
    
    return {
        "status": "success", 
        "message": "✅ ENTRY GRANTED: Ticket is valid.",
        "ticket_hash": ticket.ticket_hash
    }