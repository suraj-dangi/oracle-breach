#!/bin/bash
set -e

# Check if Company.List.txt exists
if [ ! -f "Company.List.txt" ]; then
  echo "ERROR: Company.List.txt file not found!"
  echo "Please place your Company.List.txt file in the current directory before running this script."
  echo "This file should contain the list of domains from the alleged Oracle breach (one domain per line)."
  exit 1
fi

echo "Found Company.List.txt file with the list of allegedly leaked domains."

# Create data directory and logs subdirectory if they don't exist
mkdir -p data/logs

# Build the Docker container
echo "Building Docker container..."
docker-compose build

# Index the data before starting the web application
echo "Indexing domain data..."
docker-compose run --rm webapp python /app/index_data.py /app/Company.List.txt

# Start the application
echo "Starting the web application..."
docker-compose up -d

echo "Setup complete! The application is now running at http://localhost:8080"
echo "To check logs, run: docker-compose logs -f"
echo "To stop the application, run: docker-compose down"