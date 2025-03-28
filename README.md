# Oracle Breach Domain Search Tool

This application provides a simple web interface for anyone to search if a company domain is listed in the alleged Oracle breach. It indexes domains from the Company.List.txt file and makes them searchable through a user-friendly web interface.

## Features

- Separate scripts for data indexing and web application
- Docker-based deployment for easy setup
- Persistent data storage
- Health checks and monitoring
- Search for exact and partial domain matches

## Project Structure
oracle-breach-checker/
```
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image configuration
├── index_data.py          # Script to index domain data
├── web_app.py             # Flask web application
├── run.sh                 # One-time setup script
├── Company.List.txt       # List of breached domains
└── data/                  # Persistent data storage
└── oracle_breach.db   # SQLite database (created automatically)
```

## Quick Start

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository or create the files as described
3. Run the setup script:

```bash
chmod +x run.sh
./run.sh
```

