import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.db_utils import get_new_comic_jobs, update_comic_job_status
from crawler.crawler_manager import crawl_comic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_comic_jobs():
    """
    Process all comic jobs with status "NEW".
    
    This function:
    1. Gets all comic jobs with status "NEW"
    2. For each job, updates status to "PROCESSING"
    3. Triggers the appropriate crawler
    4. Updates status to "COMPLETED" or "FAILED" based on result
    """
    logger.info("Starting comic job processing")
    
    # Get all new comic jobs
    new_jobs = get_new_comic_jobs()
    logger.info(f"Found {len(new_jobs)} new comic jobs")
    
    for job in new_jobs:
        job_id = job.id
        logger.info(f"Processing job {job_id}: {job.comic_website} - {job.comic_folder_name}")
        
        # Update status to PROCESSING
        update_comic_job_status(job_id, "PROCESSING")
        
        try:
            # Crawl the comic
            success = crawl_comic(job)
            
            # Update status based on result
            if success:
                logger.info(f"Job {job_id} completed successfully")
                update_comic_job_status(job_id, "COMPLETED")
            else:
                logger.error(f"Job {job_id} failed")
                update_comic_job_status(job_id, "FAILED")
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            update_comic_job_status(job_id, "FAILED")
    
    logger.info("Finished comic job processing")

def start_scheduler():
    """
    Start the scheduler to run the comic job processor daily.
    
    By default, it runs at 2:00 AM every day.
    """
    scheduler = BackgroundScheduler()
    
    # Schedule the job to run daily at 2:00 AM
    scheduler.add_job(
        process_comic_jobs,
        trigger=CronTrigger(second="*/10"),
        id='comic_job_processor',
        name='Process comic jobs daily',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started. Comic job processor will run daily at 2:00 AM")
    
    return scheduler

if __name__ == "__main__":
    logger.info("Comic job scheduler starting up")
    
    # Start the scheduler
    scheduler = start_scheduler()
    
    try:
        # Run the processor immediately for testing
        logger.info("Running initial job processing")
        process_comic_jobs()
        
        # Keep the script running
        logger.info("Scheduler is running. Press Ctrl+C to exit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler shutting down")
        scheduler.shutdown()