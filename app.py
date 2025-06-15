from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import smtplib
from email.message import EmailMessage
import os
import traceback

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
# Set a secret key for session management and CSRF protection
app.secret_key = os.environ.get('app_secret_key')

# --- Email Configuration ---
# Read credentials and server details from environment variables
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # Get sending email from ENV
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # Get password from ENV (use App Password for Gmail)
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL') # Get recipient email from ENV
SMTP_SERVER = os.environ.get('SMTP_SERVER') # Get SMTP server from ENV
SMTP_PORT = os.environ.get('SMTP_PORT') # Get SMTP port from ENV

# --- Basic Check (Optional but Recommended) ---
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
    print("Warning: Email environment variables are not fully configured!")
    print("Email sending will likely fail until SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT are set.")

# Ensure SMTP_PORT is an integer
try:
    SMTP_PORT = int(SMTP_PORT) if SMTP_PORT else None
except ValueError:
    print(f"Error: SMTP_PORT '{SMTP_PORT}' is not a valid integer. Setting to None.")
    SMTP_PORT = None # Set to None if invalid

# --- Routes ---

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for the blog page
@app.route('/blog')
def blog():
    return render_template('blog.html')

# --- UPDATED: Contact Form Route (Removed Subject Line Handling) ---
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # --- Process the submitted form data ---
        name = request.form.get('name')
        user_email = request.form.get('email')
        # subject = request.form.get('subject') # REMOVED SUBJECT RETRIEVAL
        message_body = request.form.get('message')

        # --- Basic Form Data Validation ---
        # Removed 'subject' from validation check
        if not name or not user_email or not message_body:
            flash('All fields (Name, Email, Message) are required. Please fill out the form completely.', 'error')
            return redirect(url_for('index', _external=True) + '#contact-form-section')

        # --- Check Email Configuration before trying to send ---
        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
            flash('Email sending is currently unavailable. Please try again later or contact us directly.', 'error')
            print("ERROR: Email configuration environment variables are not fully set up.")
            return redirect(url_for('index', _external=True) + '#contact-form-section')

        # --- Email Sending Logic ---
        msg = EmailMessage()
        # NEW SUBJECT: Default subject line as no subject field in form
        msg['Subject'] = f"New Website Inquiry from {name}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

        email_body_content = f"""
New Contact Form Submission:

Name: {name}
From Email: {user_email}
# Subject: (No subject provided by user) # Note: Subject is now automatically generated

Message:
{message_body}
"""
        msg.set_content(email_body_content)

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)

            print("\n--- Email Sent Successfully ---")
            print(f"Inquiry from {user_email} (Name: '{name}') sent to {RECIPIENT_EMAIL}")
            print("Email Sent!!\n")

            flash('Your inquiry has been sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('index', _external=True) + '#contact-form-section')

        except smtplib.SMTPAuthenticationError as auth_err:
            print(f"\n--- SMTP Authentication Error ---")
            print(f"Error: {auth_err}")
            traceback.print_exc()
            flash('Failed to send inquiry: Authentication failed. Please check sender email/password.', 'error')
            return redirect(url_for('index', _external=True) + '#contact-form-section')

        except Exception as e:
            print(f"\n--- General Error Sending Email ---")
            print(f"Could not send email for inquiry from {user_email}.")
            print(f"Error: {e}")
            traceback.print_exc()
            print("Email failed to send.\n")

            flash('There was an error sending your inquiry. Please try again.', 'error')
            return redirect(url_for('index', _external=True) + '#contact-form-section')
    
    # If it's a GET request to /contact directly, redirect to homepage
    return redirect(url_for('index'))
# --- END UPDATED Contact Route ---