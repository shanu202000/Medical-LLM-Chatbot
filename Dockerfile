FROM python:3.12-slim

WORKDIR /app

# Copy the complete project, including setup.py
COPY . .

# Install dependencies and the local project
RUN pip install --no-cache-dir -r requirements.txt

# Run Flask application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "app:app"]