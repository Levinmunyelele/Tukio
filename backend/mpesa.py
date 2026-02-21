import os
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# 1. Load Credentials
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
PASSKEY = os.getenv("MPESA_PASSKEY")
SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")

# Safaricom Sandbox URLs
AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def get_access_token():
    """Authenticates with Safaricom and returns a temporary access token."""
    try:
        res = requests.get(AUTH_URL, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
        res.raise_for_status()
        return res.json()["access_token"]
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def initiate_stk_push(phone_number: str, amount: int):
    """Triggers the M-Pesa PIN prompt on the user's phone."""
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to authenticate with Safaricom"}

    # Generate the encrypted password Safaricom requires
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = f"{SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # The payload
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://shelba-preliable-dismally.ngrok-free.dev", 
        "AccountReference": "Tukio Tickets",
        "TransactionDesc": "Event Ticket Purchase"
    }

    try:
        response = requests.post(STK_PUSH_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}