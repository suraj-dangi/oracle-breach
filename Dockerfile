FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask gunicorn && \
    apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY index_data.py /app/
COPY web_app.py /app/

# Create templates directory
RUN mkdir -p /app/templates

# Set execution permissions
RUN chmod +x /app/index_data.py /app/web_app.py

# Create data directory
RUN mkdir -p ./data

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web_app:app"]