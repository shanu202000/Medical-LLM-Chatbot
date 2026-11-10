FROM python:3.12-slim

WORKDIR /app

# First copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy application code
COPY . .

CMD ["python", "app.py"]