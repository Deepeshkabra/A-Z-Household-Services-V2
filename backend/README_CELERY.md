# Backend Jobs Implementation

This document provides instructions on how to set up and run the backend jobs for the A to Z Household Services application.

## Overview

The application includes three types of backend jobs:

1. **Daily Reminders** - Sends reminders to professionals who have pending service requests or haven't visited the platform recently.
2. **Monthly Activity Reports** - Generates and sends monthly activity reports to customers at the beginning of each month.
3. **CSV Export** - Allows admins to trigger an asynchronous job to export service requests as CSV.

## Prerequisites

- Redis server (for Celery broker and result backend)
- Python 3.x with pip

## Installation

1. Install Redis:
   - Windows: Download and install from [Redis for Windows](https://github.com/tporadowski/redis/releases)
   - Linux: `sudo apt-get install redis-server`
   - macOS: `brew install redis`

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Set environment variables in `.env` file:
   ```
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

## Running the Celery Worker

To start the Celery worker, run the following command from the backend directory:

```
celery -A celery.celery worker --loglevel=info
```

## Running the Celery Beat Scheduler

To start the Celery beat scheduler for periodic tasks, run:

```
celery -A celery.celery beat --loglevel=info
```

You can also run both the worker and beat scheduler in a single command:

```
celery -A celery.celery worker --beat --loglevel=info
```

## Implemented Jobs

### Daily Reminders

Sends reminders to professionals at 6:00 PM every day. The job checks for:
- Professionals with pending service requests
- Professionals who haven't logged in for more than 2 days

### Monthly Activity Reports

Generates and sends monthly activity reports to customers on the 1st day of every month at midnight. The report includes:
- Total service requests for the previous month
- Number of completed, cancelled, and pending requests
- Details of each service request

### CSV Export

Allows admins to trigger an asynchronous job to export service requests as CSV. The export includes:
- Service request details
- Customer information
- Service information

## API Endpoints

### Export Service Requests

```
POST /api/admin/export/service-requests
```

Request body (optional filters):
```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "service_id": 1,
  "professional_id": 2
}
```

Response:
```json
{
  "message": "CSV export job started successfully",
  "job_id": "task_id_here",
  "status": "processing"
}
```

### Check Export Status

```
GET /api/admin/export/status/{job_id}
```

Response:
```json
{
  "job_id": "task_id_here",
  "status": "completed",
  "file_url": "/api/admin/export/download/filename.csv"
}
```

### Download Export

```
GET /api/admin/export/download/{filename}
```

Returns the CSV file as an attachment.

## Troubleshooting

1. **Redis Connection Error**:
   - Ensure Redis server is running
   - Check the Redis connection URL in the .env file

2. **Celery Worker Not Starting**:
   - Check for syntax errors in the tasks.py file
   - Ensure the celery.py file is correctly configured

3. **Tasks Not Running**:
   - Check Celery worker logs for errors
   - Ensure the task is registered correctly in the Celery app

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Flask-Celery Integration](https://flask.palletsprojects.com/en/2.0.x/patterns/celery/)