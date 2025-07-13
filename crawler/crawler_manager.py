import os
import importlib
import logging
from dodo_crawl.utils.slugify import slugify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Map of website domains to crawler modules
CRAWLER_MAP = {
    'cuutruyen.net': 'dodo_crawl.crawler.crawlers.cuutruyenCrawler',
    'langgeek.net': 'dodo_crawl.crawler.crawlers.langgeekCrawler',
    'nettruyen3q.com': 'dodo_crawl.crawler.crawlers.nettruyen3qCrawler',
    'langgeek.net/invincible': 'dodo_crawl.crawler.crawlers.comicScrawlerWithUndetected',
    # Add more mappings as needed
}

def get_domain_from_url(url):
    """
    Extract domain from URL.

    Args:
        url (str): URL to extract domain from

    Returns:
        str: Domain name
    """
    # Remove protocol
    if '://' in url:
        url = url.split('://', 1)[1]

    # Remove path
    if '/' in url:
        url = url.split('/', 1)[0]

    # Remove www. prefix
    if url.startswith('www.'):
        url = url[4:]

    return url.lower()

def crawl_comic(comic_job):
    """
    Crawl a comic based on the job details.

    Args:
        comic_job (ComicJobDetail): Comic job details

    Returns:
        bool: True if crawling was successful, False otherwise
    """
    try:
        # Get domain from URL
        domain = get_domain_from_url(comic_job.comic_url)

        # Find the appropriate crawler module
        crawler_module_name = None
        for domain_pattern, module_name in CRAWLER_MAP.items():
            if domain_pattern in domain:
                crawler_module_name = module_name
                break

        if not crawler_module_name:
            logger.error(f"No crawler found for domain: {domain}")
            return False

        # Import the crawler module
        crawler_module = importlib.import_module(crawler_module_name)

        # Create folder for comic if it doesn't exist
        comic_folder = slugify(comic_job.comic_folder_name)
        os.makedirs(comic_folder, exist_ok=True)

        # All crawlers now provide a common 'crawler' function
        if hasattr(crawler_module, 'crawler'):
            # Call the crawler function with the URL and comic folder name
            crawler_module.crawler(
                comic_job.comic_url,
                comic_name=comic_folder,
                chapter_name=None  # Default to None, crawler will handle this
            )
            logger.info(f"Successfully crawled comic: {comic_folder}")

            # If this is a langgeek crawler, try to upload the zip file to R2
            if 'langgeek' in crawler_module_name:
                try:
                    from dodo_crawl.s3_API.api import upload_to_r2
                    comic_zip = f"{comic_folder}.zip"
                    upload_to_r2(comic_zip, f"comics/{comic_folder}.zip")
                    logger.info(f"Uploaded: comics/{comic_folder}.zip")
                except Exception as e:
                    logger.error(f"Failed to upload to R2: {e}")
        else:
            logger.error(f"Unsupported crawler interface for {domain}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error crawling comic: {e}")
        return False
