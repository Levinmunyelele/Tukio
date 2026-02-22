import qrcode
import os

# Create a folder to store the generated tickets if it doesn't exist
TICKET_DIR = "tickets"
os.makedirs(TICKET_DIR, exist_ok=True)

def generate_ticket_qr(ticket_id: str, phone_number: str):
    """Generates a QR code for a ticket and saves it locally."""
    
    # The data the bouncer will see when they scan it
    qr_data = f"TUKIO-TICKET|ID:{ticket_id}|PHONE:{phone_number}"
    
    # Create the QR instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create the image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the file
    file_path = f"{TICKET_DIR}/ticket_{ticket_id}.png"
    img.save(file_path)
    
    return file_path