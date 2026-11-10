FROM python:3.12-slim

WORKDIR /app

# Copy the complete project, including setup.py
COPY . .

# Install dependencies and the local project
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
