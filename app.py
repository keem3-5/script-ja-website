from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
from email.message import EmailMessage

# Initialize the Flask application
app = Flask(__name__)

# Flask secret key for session management and CSRF protection
# IMPORTANT: This MUST be set as an environment variable in production (e.g., in Cloud Run settings).
# Without it, session management and CSRF protection will not work securely.
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# --- Configuration ---
# Read credentials and server details from environment variables
# These variables MUST be set in your production environment (e.g., Cloud Run environment variables).

SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # For production, use secure secrets management (e.g., Cloud Secret Manager)
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT_STR = os.environ.get('SMTP_PORT')

# Ensure SMTP_PORT is an integer
SMTP_PORT = None
if SMTP_PORT_STR:
    try:
        SMTP_PORT = int(SMTP_PORT_STR)
    except ValueError:
        print(f"ERROR: SMTP_PORT '{SMTP_PORT_STR}' is not a valid integer. Email sending will fail.")
else:
    print("ERROR: SMTP_PORT environment variable is not set. Email sending will fail.")

# --- Routes ---

@app.route('/')
def index():
    """
    Renders the main landing page.
    This page displays the logo area and the scroll-down button.
    It also contains the services section further down the page.
    """
    return render_template('index.html')

@app.route('/contact/<service_type>', methods=['GET', 'POST'])
def contact(service_type):
    """
    Handles displaying and processing the contact form for a specific service.
    Args:
        service_type (str): The type of service the user is inquiring about
                            (e.g., 'accounting', 'legal document preparation').
    """
    valid_services = ['Accounting', 'Legal Document Preparation']
    if service_type.lower() not in valid_services:
        flash(f"Invalid service type: {service_type}.", 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message')

        # Basic validation for form fields
        if not all([user_email, subject, message_body]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('contact', service_type=service_type))

        # Check if email configuration is complete before attempting to send
        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT]):
            flash('Server email configuration incomplete. Cannot send inquiry.', 'error')
            print("ERROR: Email sending configuration is incomplete. Check environment variables.")
            return redirect(url_for('contact', service_type=service_type))

        # --- Email Sending Logic ---
        msg = EmailMessage()
        msg['Subject'] = f"Script Technologies Jamaica Service Inquiry: {service_type.capitalize()} - {subject}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Reply-To'] = user_email # Set Reply-To to the user's email

        email_body_content = f"""
Service Type: {service_type.capitalize()}
From Name: {user_name if user_name else 'N/A'}
From Email: {user_email}
Subject: {subject}

Message:
{message_body}
"""
        msg.set_content(email_body_content)

        server = None # Initialize server to None
        try:
            if SMTP_PORT == 465:
                # Use SMTP_SSL for port 465 (often for implicit SSL)
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
            else:
                # Use SMTP + starttls() for other ports like 587 (explicit TLS)
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                server.starttls() # Secure the connection

            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

            flash('Your inquiry has been sent successfully!', 'success')
            return redirect(url_for('index'))

        except smtplib.SMTPAuthenticationError as e:
            print(f"ERROR: SMTP Authentication Failed. Check SENDER_EMAIL and SENDER_PASSWORD (App Password?). Error: {e}")
            flash('Authentication error: Could not log in to email server. Please check credentials.', 'error')
        except smtplib.SMTPServerDisconnected as e:
            print(f"ERROR: SMTP Server Disconnected unexpectedly. Check server address, port, or SSL/TLS setup. Error: {e}")
            flash('Connection error: Email server disconnected. Please try again.', 'error')
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
            if server: # Ensure server object exists before trying to quit
                try:
                    server.quit()
                except Exception as e:
                    print(f"Error quitting SMTP server: {e}") # Log only, don't re-raise

        # If we reach here, an error occurred during POST request, redirect back
        return redirect(url_for('index'))

    # If it's a GET request, render the contact form
    display_service_type = service_type.capitalize()
    return render_template('contact.html', service_type=display_service_type)


if __name__ == '__main__':
    # When deploying to Cloud Run, the 'PORT' environment variable is automatically provided.
    # For local development, it defaults to 8080.
    port = int(os.environ.get('PORT', 8080))
    # In production, debug=False is crucial for security and performance.
    # On Cloud Run, 'host' is not typically needed; it listens on the assigned port.
    app.run(debug=False, port=port)
# Note: In production, ensure to set the environment variables securely.
# This includes using Cloud Secret Manager for sensitive data like passwords.
