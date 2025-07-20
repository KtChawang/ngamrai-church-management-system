import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

# === CONFIGURE ME ===
EMAIL_SENDER = "ngam.ch17@gmail.com"
EMAIL_RECEIVER = "ngam.ch17@gmail.com"
APP_PASSWORD = "ozckfdrlqryewrwh"
PROJECT_DIR = Path(r"C:\Users\USER\Church Management System\backups")
SUBJECT = "📦 Weekly Church Backup"

# === Locate most recent backup ===
def get_latest_backup(folder):
    backups = list(folder.glob("*"))
    if not backups:
        return None
    latest = max(backups, key=os.path.getctime)
    return latest

latest_file = get_latest_backup(PROJECT_DIR)
if not latest_file:
    print("❌ No backup file found.")
    exit()

# === Build the email ===
msg = EmailMessage()
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER
msg["Subject"] = SUBJECT
msg.set_content(f"Attached is the latest backup: {latest_file.name}")

with open(latest_file, "rb") as f:
    file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=latest_file.name)

# === Send the email ===
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(EMAIL_SENDER, APP_PASSWORD)
    server.send_message(msg)

print("✅ Backup emailed successfully.")
