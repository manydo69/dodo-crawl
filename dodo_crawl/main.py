import argparse
import logging

from dodo_crawl.scheduler.scheduler import start_scheduler, process_comic_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("comic_crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the comic crawler application.

    Supports two modes:
    1. scheduler: Start the scheduler to run daily
    2. process: Process all new comic jobs immediately
    """
    parser = argparse.ArgumentParser(description='Comic Crawler Application')
    parser.add_argument('mode', choices=['scheduler', 'process'], 
                        help='Mode to run the application in')

    args = parser.parse_args()

    if args.mode == 'scheduler':
        logger.info("Starting scheduler mode")
        scheduler = start_scheduler()

        try:
            # Keep the script running
            logger.info("Scheduler is running. Press Ctrl+C to exit")
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler shutting down")
            scheduler.shutdown()

    elif args.mode == 'process':
        logger.info("Starting process mode")
        process_comic_jobs()
        logger.info("Processing completed")

if __name__ == "__main__":
    main()
