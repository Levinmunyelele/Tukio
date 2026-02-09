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
    
    subgraph "Payment Flow"
    API -->|Initiate Payment| MPesa[Safaricom Daraja API]
    MPesa -->|STK Push| UserPhone[User's Phone]
    MPesa -->|Webhook Callback| API
    end
    
    subgraph "Data & Logic"
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Generate| QR[QR Code Service]
    end

Technical DecisionsFastAPI (Backend): Chosen for its asynchronous capabilities, essential for handling high-concurrency ticket sales and M-Pesa webhooks without blocking.PostgreSQL: Relational integrity was crucial for financial transactions (tickets/payments).React + Tailwind: Ensures a lightweight, mobile-responsive experience for users on low-bandwidth connections.🗄️ Database SchemaThe database is designed to handle high-throughput transactions with strict relational integrity.TableDescriptionKey ColumnsUsersStores event organizers and attendees.id, email, password_hash, roleEventsEvent details and capacity management.id, organizer_id, title, price, capacityTicketsThe core asset. Links a user to an event.id, event_id, user_id, qr_hash, status (VALID/USED)TransactionsAudit log for M-Pesa payments.id, mpesa_receipt_number, amount, phone_number🔌 API Documentation (Core Endpoints)1. Payment & TicketingPOST /api/tickets/purchase: Initiates the M-Pesa STK Push.Payload: { "event_id": 12, "phone": "2547..." }POST /api/hooks/mpesa: (Critical) The callback URL that Safaricom hits to confirm payment. Triggers ticket generation.2. Validation (Gatekeeper)GET /api/tickets/validate/{qr_hash}: Checks if a ticket is valid.Logic: If status is VALID, change to USED and return Success. If USED, return Error (Duplicate Entry).💻 Local Development SetupPrerequisitesNode.js & npmPython 3.9+PostgreSQLNgrok (For testing M-Pesa Webhooks locally)1. Backend SetupBash# Clone repository
git clone [https://github.com/Levinmunyelele/Tukio.git](https://github.com/Levinmunyelele/Tukio.git)
cd Tukio/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
2. Frontend SetupBashcd ../frontend
npm install
npm run dev
3. Environment Variables (.env)Create a .env file in the backend folder:Code snippetDATABASE_URL=postgresql://user:pass@localhost/tukio_db
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_PASSKEY=your_passkey
SECRET_KEY=your_jwt_secret
🚧 Roadmap[x] Database Design & Schema[x] FastAPI Project Structure[ ] M-Pesa Sandbox Integration[ ] QR Code Generation Service[ ] React Dashboard UI[ ] Email Notification System📞 ContactLevin Munyelele Full-Stack Developer | Data Scientist
