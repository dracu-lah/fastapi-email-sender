from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
import smtplib
import os
import tempfile

app = FastAPI(title="Email Sender API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - change this in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/send-email")
async def send_email(
    email: str = Form(...),
    app_password: str = Form(...),
    recipients: str = Form(...),  # comma-separated list
    subject: str = Form(...),
    body: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # Save resume temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume.filename)[1]) as tmp:
            tmp.write(await resume.read())
            tmp_path = tmp.name

        # Build email
        msg = EmailMessage()
        msg["From"] = email
        msg["To"] = ", ".join([r.strip() for r in recipients.split(",")])
        msg["Subject"] = subject
        msg.set_content(body)

        # Attach resume
        with open(tmp_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=resume.filename)

        # Send email securely
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, app_password)
            smtp.send_message(msg)

        os.remove(tmp_path)
        return JSONResponse({"status": "success", "message": "✅ Email sent successfully!"})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
