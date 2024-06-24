#!/bin/bash
set -e

# Start the main PostgreSQL entrypoint script
/usr/local/bin/docker-entrypoint.sh postgres &

# Wait for PostgreSQL to be ready
/wait-for-it.sh localhost:5432 -t 60

# Run the Python script
python3 /docker-entrypoint-initdb.d/database.py

# Keep the container running
wait