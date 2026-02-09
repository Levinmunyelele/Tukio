# 🎟️ Tukio: Event Ticketing & Management Platform

![Status](https://img.shields.io/badge/Status-In%20Development-green)
![Stack](https://img.shields.io/badge/Tech-React%20%7C%20FastAPI%20%7C%20PostgreSQL-blue)
![Payment](https://img.shields.io/badge/Payment-M--Pesa%20Daraja%20API-red)

**Tukio** (Swahili for *Event*) is a modern, mobile-first ticketing platform tailored for the African market. It solves the problem of fraudulent ticketing and manual payments by integrating **M-Pesa STK Push** for instant payments and generating cryptographically secure **QR Codes** for entry validation.

---

## 🚀 Key Features

* **⚡ Instant M-Pesa Payments:** Seamless integration with Safaricom Daraja API (STK Push) for friction-less checkout.
* **🔒 Secure QR Ticketing:** Each ticket generates a unique, signed QR code that can only be scanned once.
* **📊 Organizer Dashboard:** Real-time analytics on ticket sales, revenue, and attendance.
* **📱 Gatekeeper Mode:** A dedicated mobile interface for event bouncers to scan and validate tickets in <1 second.
* **📩 Automated Delivery:** Tickets are emailed instantly upon successful payment callback.

---

## 🏗️ System Architecture

The system follows a micro-service inspired architecture to separate concerns between payment processing, core application logic, and the user interface.

```mermaid
graph TD
    User[End User] -->|Browses Events| Client[React Frontend]
    Client -->|API Requests| API[FastAPI Backend]
    
    subgraph Payment ["Payment Flow"]
    API -->|Initiate Payment| MPesa[Safaricom Daraja API]
    MPesa -->|STK Push| UserPhone[User's Phone]
    MPesa -->|Webhook Callback| API
    end
    
    subgraph Data ["Data & Logic"]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Generate| QR[QR Code Service]
    end
```
---

## Technical Decisions
**FastAPI (Backend)**: Chosen for its asynchronous capabilities, essential for handling high-concurrency ticket sales and M-Pesa webhooks without blocking.

**PostgreSQ**L: Relational integrity was crucial for financial transactions (tickets/payments).

**React + Tailwind**: Ensures a lightweight, mobile-responsive experience for users on low-bandwidth connections.

---

## 🗄️ Database Schema

The database follows a normalized relational structure to ensure data integrity for financial transactions.

```mermaid
erDiagram
    USERS ||--o{ EVENTS : organizes
    USERS ||--o{ TICKETS : buys
    EVENTS ||--o{ TICKETS : contains
    TICKETS ||--|| TRANSACTIONS : generated_from

    USERS {
        int id PK
        string email
        string role "organizer/attendee"
        string password_hash
    }

    EVENTS {
        int id PK
        int organizer_id FK
        string title
        decimal price
        int capacity
    }

    TICKETS {
        int id PK
        int event_id FK
        int user_id FK
        string qr_hash "Unique encrypted string"
        string status "VALID/USED"
    }

    TRANSACTIONS {
        int id PK
        string mpesa_receipt "e.g. QWE123RTY"
        decimal amount
        string phone_number
    }
```
---
### 📝 Database Table Details

| Table | Role | Key Fields & Constraints |
| :--- | :--- | :--- |
| **Users** | Manages authentication and authorization. | `id` (PK), `email` (Unique), `role` (Enum: 'admin', 'organizer', 'user'). |
| **Events** | Stores event metadata managed by organizers. | `organizer_id` (FK -> Users), `capacity` (Integer), `price` (Decimal). |
| **Tickets** | The core asset linking a User to an Event. | `qr_hash` (Unique Index), `status` (Enum: 'VALID', 'USED'), `event_id` (FK). |
| **Transactions** | Audit log for M-Pesa payments. | `mpesa_receipt_number` (Unique), `amount`, `phone_number`. |
---

## 🔌 API Documentation (Core Endpoints)
### 1. Payment & Ticketing
```POST /api/tickets/purchase```: Initiates the M-Pesa STK Push.

    Payload:```{ "event_id": 12, "phone": "2547..." }```

```POST /api/hooks/mpesa```: (Critical) The callback URL that Safaricom hits to confirm payment. Triggers ticket generation.

### 2. Validation (Gatekeeper)
```GET /api/tickets/validate/{qr_hash}```: Checks if a ticket is valid.

     Logic: If status is ```VALID```, change to ```USED``` and return Success. If ```USED```, return Error (Duplicate Entry).

     ---
## 💻 Local Development Setup
Prerequisites
Node.js & npm
Python 3.9+
PostgreSQL
Ngrok (For testing M-Pesa Webhooks locally)

### 1. Backend Setup
#### Clone repository
```git clone [https://github.com/Levinmunyelele/Tukio.git](https://github.com/Levinmunyelele/Tukio.git)
cd Tukio/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```
---
### 2. Fronend Setup
```cd ../frontend
npm install
npm run dev
```
---
### 3. Environment Variables (.env)
Create a .env file in the backend folder:
```DATABASE_URL=postgresql://user:pass@localhost/tukio_db
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_PASSKEY=your_passkey
SECRET_KEY=your_jwt_secret
```
---
## 🚧 Project Roadmap

### Phase 1: Core Architecture (Current Status)
- [x] **Database Design:** Normalized schema for Users, Events, and Tickets.
- [x] **Backend Setup:** FastAPI project structure with SQLAlchemy and Alembic migrations.
- [x] **Authentication:** JWT-based login for Organizers and Staff.
- [ ] **M-Pesa Integration:** Implement STK Push and Callback handling (Webhooks).

### Phase 2: The Ticket Engine
- [ ] **QR Service:** Generate cryptographically signed QR codes for each ticket.
- [ ] **Validation API:** Endpoint for bouncers to scan and verify tickets.
- [ ] **Email Service:** Auto-send tickets to users after payment confirmation.

### Phase 3: Frontend & UI
- [ ] **Organizer Dashboard:** React charts showing sales and revenue.
- [ ] **Public Event Page:** Mobile-responsive page for users to buy tickets.
- [ ] **Gatekeeper App:** Simple mobile view for scanning QR codes at the door.

## 📞 Contact

**Levin Munyelele** Full-Stack Developer | Data Scientist  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/levin-munyelele/) [![Portfolio]

(https://img.shields.io/badge/Portfolio-View%20Projects-teal?style=for-the-badge&logo=github)](https://levinmunyelele.github.io/portfolio/)

📧 **Email:** [munyelelelevin@gmail.com](mailto:munyelelelevin@gmail.com)


