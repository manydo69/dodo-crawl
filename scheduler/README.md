# Comic Crawler Scheduler

This directory contains the scheduler component of the comic crawler application. The scheduler periodically checks for new comic jobs and processes them using the appropriate crawler.

## Local Development

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- Chrome browser

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with database connection details:
   ```
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=comic_crawler
   ```

3. Run the scheduler:
   ```bash
   python main.py scheduler
   ```

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Build and run the containers:
   ```bash
   docker-compose up -d
   ```

2. Check the logs:
   ```bash
   docker-compose logs -f scheduler
   ```

3. Stop the containers:
   ```bash
   docker-compose down
   ```

## Google Cloud Deployment

For detailed instructions on deploying the scheduler to Google Cloud Platform, see [gcp_deployment_guide.md](gcp_deployment_guide.md).

### Quick Reference

1. Set up a PostgreSQL database using Cloud SQL
2. Create a Compute Engine VM with Chrome installed
3. Clone the repository and install dependencies
4. Configure environment variables
5. Set up persistent storage for comic files
6. Run the scheduler as a systemd service

## Configuration

The scheduler can be configured using environment variables:

- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: PostgreSQL database name

## Usage

The scheduler supports two modes:

1. `scheduler`: Start the scheduler to run periodically
   ```bash
   python main.py scheduler
   ```

2. `process`: Process all new comic jobs immediately and exit
   ```bash
   python main.py process
   ```

## Monitoring

The scheduler logs to both the console and a file (`scheduler.log`). You can monitor the logs to track the progress of comic jobs.

For Google Cloud deployments, you can use Cloud Monitoring and Cloud Logging for more advanced monitoring and alerting.