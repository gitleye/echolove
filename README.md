# ECHOLOVE

Curate under-the-radar tools by **echoing** genuine love from public, verifiable sources.

## Overview

This project provides a small yet scalable backend for discovering and serving information about lesser‑known tools and software. It collects data from public APIs such as Hacker News, Stack Exchange, and GitHub, stores that data in a database, and exposes an HTTP API via FastAPI.

### Features

* **Automated ingestion:** A Python script fetches potential tools from multiple sources using their public APIs. It normalizes the data, stores it in a SQLite database by default, and marks reviews as archived if their source links disappear.
* **Transparency:** Each tool record includes a table of origins and reviews, making it clear where the information came from. The ingestion script ensures no duplicate records and keeps track of when each review was last checked.
* **Simple API:** Using FastAPI, the service exposes endpoints to list tools, query by text or tags, retrieve specific tools by slug, and view all reviews.
* **Deployable anywhere:** Provided Dockerfile allows you to containerize the application and run it locally, on AWS ECS/Fargate, GCP Cloud Run, or other platforms. The `.env.example` file shows configuration options such as database connection and API keys for external services.

## Getting started

1. Copy the example configuration:

```bash
cp .env.example .env
```

2. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the initial ingestion to populate your database:

```bash
python -m app.ingest
```

4. Start the API server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Use `/tools` to list all tools, optionally filtering by query string or tag.

## Docker usage

To build and run the application in Docker:

```bash
docker build -t echolove:dev .
docker run -p 8080:8080 --env-file .env echolove:dev
```

## Cloud deployment

This project can be deployed on AWS Fargate/ECS or Google Cloud Run. Use the same Docker image for both. See the README in the root for instructions on setting environment variables and scheduling the ingestion job using EventBridge or Cloud Scheduler.

## Contributing

Feel free to extend the data sources by implementing additional adapters in `app/sources/`. Each adapter should subclass `SourceAdapter` and yield normalized tool data. Contributions are welcome!