from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import smtplib
from email.message import EmailMessage
import os
import traceback # Added this previously for better error logging

# Initialize the Flask application
app = Flask(__name__)

app.secret_key = os.environ.get('app_secret_key') # Set a secret key for session management and CSRF protection
# --- Configuration ---

# --- Email Configuration ---
# Read credentials and server details from environment variables

SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # Get sending email from ENV
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # Get password from ENV (use Secrets in production)
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL') # Get recipient email from ENV
SMTP_SERVER = os.environ.get('SMTP_SERVER') # Get SMTP server from ENV
SMTP_PORT = os.environ.get('SMTP_PORT') # Get SMTP port from ENV

# --- Basic Check (Optional but Recommended) ---
# Add checks to ensure the variables are set, especially in production
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
    print("Warning: Email environment variables are not fully configured!")
    print("Email sending will likely fail until SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT are set.")
# --- End Basic Check ---


# Ensure SMTP_PORT is an integer
try:
    SMTP_PORT = int(SMTP_PORT) if SMTP_PORT else None
except ValueError:
    print(f"Error: SMTP_PORT '{SMTP_PORT}' is not a valid integer.")
    SMTP_PORT = None # Set to None if invalid


# --- Routes ---

# Route for the homepage
@app.route('/')
def index():
    """
    Renders the main landing page.
    This page displays the logo area and the scroll-down button.
    It also contains the services section further down the page.
    """
    return render_template('index.html')


# --- NEW: Placeholder Blog Route ---
@app.route('/blog')
def blog():
    return render_template('blog.html')
# --- END NEW ---

# Route for handling contact form submissions

@app.route('/contact/<service_type>', methods=['GET', 'POST'])
def contact(service_type):
    """
    Handles displaying and processing the contact form for a specific service.
    Args:
        service_type (str): The type of service the user is inquiring about
                            (e.g., 'accounting', 'legal document preparation services').
    """
    # Validate service_type from URL path for GET requests as well
    # --- CHANGE 1: Update the valid_services list ---
    valid_services = ['accounting', 'legal document preparation services']
    if service_type.lower() not in valid_services:
        flash('Invalid service type specified.', 'error') # Optional: give feedback
        return redirect(url_for('index'))

    # --- CHANGE 2: Use .title() for proper capitalization of multiple words ---
    # service_type will be URL-decoded (e.g., "legal document preparation services")
    # .title() will correctly capitalize each word ("Legal Document Preparation Services")
    display_service_type = service_type.title() # Changed from .capitalize()

    if request.method == 'POST':
        # --- Process the submitted form data ---
        user_email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message')

        # --- Basic Form Data Validation ---
        if not user_email or not subject or not message_body:
            flash('All fields (Email, Subject, Message) are required. Please fill out the form completely.', 'error')
            return render_template('contact.html',
                                   service_type=display_service_type, # Use display_service_type here
                                   user_email=user_email if user_email else '',
                                   subject=subject if subject else '',
                                   message_body=message_body if message_body else '')

        # --- Check Email Configuration before trying to send ---
        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
            flash('Email sending is currently unavailable. Please try again later or contact us directly.', 'error')
            print("ERROR: Email configuration environment variables are not fully set up.")
            return render_template('contact.html',
                                   service_type=display_service_type, # Use display_service_type here
                                   user_email=user_email,
                                   subject=subject,
                                   message_body=message_body)


        # --- Email Sending Logic ---
        msg = EmailMessage()
        # --- CHANGE 3: Ensure subject line uses the title-cased service type ---
        msg['Subject'] = f"ScriptJa Service Inquiry: {display_service_type} - {subject}" # Changed from service_type.capitalize()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

        email_body_content = f"""
Service Type: {display_service_type} # --- CHANGE 4: Use display_service_type here too ---
From Email: {user_email}
Subject: {subject}

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
            print(f"Inquiry for {service_type} from {user_email} sent to {RECIPIENT_EMAIL}") # This line is fine, service_type is the raw URL value
            print("Email Sent!!\n")

            flash('Your inquiry has been sent successfully!', 'success')
            return redirect(url_for('index'))

        except smtplib.SMTPAuthenticationError as auth_err: # Catch specific auth error
            print(f"\n--- SMTP Authentication Error ---")
            print(f"Error: {auth_err}")
            import traceback
            traceback.print_exc()
            flash('Failed to send inquiry: Authentication failed. Please check sender email/password.', 'error')
            return render_template('contact.html',
                                   service_type=display_service_type, # Use display_service_type here
                                   user_email=user_email,
                                   subject=subject,
                                   message_body=message_body)

        except Exception as e:
            print(f"\n--- General Error Sending Email ---")
            print(f"Could not send email for {service_type} inquiry.") # This line is fine
            print(f"Error: {e}")
            import traceback
            traceback.print_exc() # Print full traceback
            print("Email failed to send.\n")

            flash('There was an error sending your inquiry. Please try again.', 'error')
            return render_template('contact.html',
                                   service_type=display_service_type, # Use display_service_type here
                                   user_email=user_email,
                                   subject=subject,
                                   message_body=message_body)


    # For GET requests or if POST conditions were not met (e.g. initial page load)
    return render_template('contact.html', service_type=display_service_type)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)