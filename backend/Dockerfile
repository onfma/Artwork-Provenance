# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir pydantic_settings

# Copy the application code
COPY . .

# RUN THE DATA IMPORT SCRIPT DURING BUILD
# This downloads the Romanian heritage data and saves it to data/romanian_heritage.nt
# inside the image. This ensures data is available immediately upon deployment.
RUN python scripts/import_romanian_heritage.py

# Expose the port (8000 is standard for FastAPI/Uvicorn)
EXPOSE 8000

# Command to run the app (Update 'app.main:app' to your actual entry point)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
