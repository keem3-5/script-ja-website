
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import smtplib
from email.message import EmailMessage
import os 

from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
from email.message import EmailMessage # This is the correct import for EmailMessage

# Initialize the Flask application
app = Flask(__name__)

# Flask secret key for session management and CSRF protection
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_dev') # Added a more descriptive name and a default

# --- Configuration ---
# Read credentials and server details from environment variables

SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # Use Secrets in production, App Passwords for Gmail
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT_STR = os.environ.get('SMTP_PORT') # Read as string initially

# --- Basic Check (Optional but Recommended) ---
print("\n--- Email Configuration Check ---")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")
# WARNING: Do NOT print SENDER_PASSWORD in production logs for security!
# print(f"SENDER_PASSWORD: {'*' * len(SENDER_PASSWORD) if SENDER_PASSWORD else 'Not Set'}")
print(f"RECIPIENT_EMAIL: {RECIPIENT_EMAIL}")
print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_PORT (string): {SMTP_PORT_STR}")

if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT_STR]):
    print("WARNING: Email environment variables are NOT fully configured! Email sending will likely fail.")
else:
    print("Email environment variables appear to be set.")
print("--- End Email Configuration Check ---\n")

# Ensure SMTP_PORT is an integer
SMTP_PORT = None
try:
    if SMTP_PORT_STR:
        SMTP_PORT = int(SMTP_PORT_STR)
    else:
        print("Error: SMTP_PORT environment variable is not set.")
except ValueError:
    print(f"Error: SMTP_PORT '{SMTP_PORT_STR}' is not a valid integer. Set to None.")
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

# Route for handling contact form submissions
@app.route('/contact/<service_type>', methods=['GET', 'POST'])
def contact(service_type):
    """
    Handles displaying and processing the contact form for a specific service.
    Args:
        service_type (str): The type of service the user is inquiring about
                            (e.g., 'accounting', 'legal').
    """
    valid_services = ['accounting', 'legal']
    if service_type.lower() not in valid_services:
        # Redirect to homepage if service_type is not valid
        flash(f"Invalid service type: {service_type}.", 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # --- Process the submitted form data ---
        user_name = request.form.get('name') # Assuming you might add a 'name' field
        user_email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message')

        print(f"--- Processing Contact Form for {service_type.capitalize()} ---")
        print(f"User Email: {user_email}, Subject: {subject}")

        # Basic validation for form fields
        if not all([user_email, subject, message_body]):
            flash('Please fill in all required fields.', 'error')
            print("ERROR: Missing form fields.")
            return redirect(url_for('contact', service_type=service_type))

        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
            flash('Email sending is not configured correctly on the server.', 'error')
            print("ERROR: Email sending configuration is incomplete. Check environment variables and SMTP_PORT conversion.")
            return redirect(url_for('contact', service_type=service_type))


        # --- Email Sending Logic ---
        msg = EmailMessage()
        msg['Subject'] = f"ScriptJa Service Inquiry: {service_type.capitalize()} - {subject}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        # Optionally add Reply-To header so you can easily reply to the user
        msg['Reply-To'] = user_email

        email_body_content = f"""
Service Type: {service_type.capitalize()}
From Name: {user_name if user_name else 'N/A'}
From Email: {user_email}
Subject: {subject}

Message:
{message_body}
"""
        msg.set_content(email_body_content)

        try:
            print(f"Attempting to connect to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
            server = None
            if SMTP_PORT == 465:
                # Use SMTP_SSL for port 465 (often for implicit SSL)
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
            else:
                # Use SMTP + starttls() for other ports like 587 (explicit TLS)
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                server.starttls() # Secure the connection

            print(f"Logging in as {SENDER_EMAIL}...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("SMTP login successful.")

            server.send_message(msg)
            print(f"Email sent successfully to {RECIPIENT_EMAIL} for service '{service_type}'.")
            print("--- Email Sent Successfully ---\n")

            flash('Your inquiry has been sent successfully!', 'success')
            return redirect(url_for('index'))

        except smtplib.SMTPAuthenticationError as e:
            print(f"ERROR: SMTP Authentication Failed. Check SENDER_EMAIL and SENDER_PASSWORD. Error: {e}")
            flash('Authentication error: Check sender email or password.', 'error')
        except smtplib.SMTPServerDisconnected as e:
            print(f"ERROR: SMTP Server Disconnected unexpectedly. This often means incorrect port or SSL/TLS setup. Error: {e}")
            flash('Connection error: SMTP server disconnected. Please try again.', 'error')
        except smtplib.SMTPConnectError as e:
            print(f"ERROR: SMTP Connection Error. Could not connect to the server. Check SMTP_SERVER and SMTP_PORT. Error: {e}")
            flash('Connection error: Could not reach email server. Please try again.', 'error')
        except smtplib.SMTPException as e:
            print(f"ERROR: General SMTP error. Error: {e}")
            flash('An email sending error occurred. Please try again.', 'error')
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while sending email: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
        finally:
            if server:
                try:
                    server.quit()
                    print("SMTP connection closed.")
                except Exception as e:
                    print(f"Error quitting SMTP server: {e}")

        # If we reach here, an error occurred, redirect back
        return redirect(url_for('index'))

    # If it's a GET request, render the contact form
    display_service_type = service_type.capitalize()
    return render_template('contact.html', service_type=display_service_type)


if __name__ == '__main__':
    # Flask provides the PORT environment variable in production environments like Cloud Run
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
