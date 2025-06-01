
FROM python:3.12-slim


WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes app.py and the 'templates' folder
COPY . .

# Set a default PORT environment variable. Cloud Run will override this.
ENV PORT 8080


# $PORT is automatically set by Cloud Run
# Explicitly use sh -c and print PORT for debugging purposes
CMD sh -c "echo 'DEBUG: PORT is set to: '$PORT && gunicorn -w 4 -b 0.0.0.0:${PORT} app:app"
