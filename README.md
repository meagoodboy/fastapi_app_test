# Test application
A simple fastapi-psql app to test out the concepts covered

## Prerequisites
Make sure a postgress service is running and is on the same network(update the docker compose)

## Settings
place the following file in the main folder(where main.py is present)
```
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database_name>
POSTGRES_SERVICE=<service_name as per the container>
POSTGRES_PORT=<port as per the psql service>
```

## Running the app
run the following commands
```
docker compose build
docker compose up
```