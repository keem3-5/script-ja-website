from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import smtplib
from email.message import EmailMessage
import os 

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
    # In a production app, you might want to raise an error or log more critically
    # if app.env == 'production': # Check Flask environment if configured
    #    raise ValueError("Email environment variables must be set in production!")
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

# Route for handling contact form submissions

@app.route('/contact/<service_type>', methods=['GET', 'POST'])
def contact(service_type):
    """
    Handles displaying and processing the contact form for a specific service.
    Args:
        service_type (str): The type of service the user is inquiring about
                            (e.g., 'accounting', 'legal').
    """
    if request.method == 'POST':
        # --- Process the submitted form data ---

        
        user_email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message') # Renamed to avoid conflict with EmailMessage

        # --- Email Sending Logic ---
        # Create the email content
        msg = EmailMessage()
        msg['Subject'] = f"ScriptJa Service Inquiry: {service_type.capitalize()} - {subject}"
        # It's better to set the 'From' field to your sending email, and include
        # the user's email in the body or as a Reply-To header.
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

       
        email_body_content = f"""
Service Type: {service_type.capitalize()}
From Email: {user_email}
Subject: {subject}

Message:
{message_body}
"""
        msg.set_content(email_body_content)

        try:
            
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)

            print("\n--- Email Sent Successfully ---")
            print(f"Inquiry for {service_type} from {user_email} sent to {RECIPIENT_EMAIL}")
            print("Email Sent!!\n")

            # Redirect to a success page or the homepage
            flash('Your inquiry has been sent successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            # Log the error and perhaps redirect to an error page
            print(f"\n--- Error Sending Email ---")
            print(f"Could not send email for {service_type} inquiry.")
            print(f"Error: {e}")
            print("Email failed to send.\n")

            flash('There was an error sending your inquiry. Please try again.', 'error')
            # For now, redirect home even on error
            return redirect(url_for('index'))


    
 
    valid_services = ['accounting', 'legal']
    if service_type.lower() not in valid_services:
        
        return redirect(url_for('index')) 

   
    display_service_type = service_type.capitalize()

    return render_template('contact.html', service_type=display_service_type)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080)) 
    app.run(debug=True, host='0.0.0.0', port=port)
