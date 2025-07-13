# Dodo Crawl

A comic crawler application that can download comics from various websites.

## Installation

### From Source

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dodo-crawl.git
   cd dodo-crawl
   ```

2. Install the package in development mode:
   ```
   pip install -e .
   ```

### Using pip

```
pip install dodo-crawl
```

## Usage

The application supports two modes:

1. **Scheduler Mode**: Start the scheduler to run daily
   ```
   dodo-crawl scheduler
   ```

2. **Process Mode**: Process all new comic jobs immediately
   ```
   dodo-crawl process
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_ACCOUNT_ID=your_account_id
R2_BUCKET_NAME=your_bucket_name
COMIC_DIR=path_to_save_comics
```

## Development

### Project Structure

- `dodo_crawl/`: Main package
  - `crawler/`: Comic crawler modules
    - `crawlers/`: Individual crawler implementations
    - `hook_js/`: JavaScript hooks for crawlers
  - `s3_API/`: API for S3/R2 storage
  - `utils/`: Utility functions
  - `entity/`: Entity classes
  - `scheduler/`: Scheduler for running jobs

### Adding a New Crawler

1. Create a new crawler module in `dodo_crawl/crawler/crawlers/`
2. Implement the `ComicCrawler` interface
3. Add the crawler to the `CRAWLER_MAP` in `dodo_crawl/crawler/crawler_manager.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.