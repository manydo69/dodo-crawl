import os
import importlib
import logging
from utils.slugify import slugify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Map of website domains to crawler modules
CRAWLER_MAP = {
    'cuutruyen.net': 'crawler.crawlers.cuutruyenCrawler',
    'langgeek.net': 'crawler.crawlers.humanLikeCrawler',
    'nettruyen3q.com': 'crawler.crawlers.nettruyen3qCrawler',
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
        
        # Handle different crawler interfaces
        if domain_pattern == 'cuutruyen.net':
            # cuutruyenCrawler has a single crawler function
            crawler_module.crawler(comic_job.comic_url)
        elif domain_pattern == 'langgeek.net':
            # humanLikeCrawler has separate functions for chapters and images
            all_chapters = crawler_module.get_chapter_list(comic_job.comic_url)
            for chapter_name, chapter_url in all_chapters:
                crawler_module.download_images_from_chapter(
                    slugify(chapter_name), 
                    chapter_url, 
                    save_root=comic_folder
                )
                crawler_module.random_pause()
            
            # Zip the comic folder
            comic_zip = f"{comic_folder}.zip"
            crawler_module.zip_folder(comic_folder)
            
            # Upload to R2 if available
            try:
                from s3_API.api import upload_to_r2
                upload_to_r2(comic_zip, f"comics/{comic_folder}.zip")
                logger.info(f"Uploaded: comics/{comic_folder}.zip")
            except Exception as e:
                logger.error(f"Failed to upload to R2: {e}")
        else:
            # For other crawlers, try to find a common interface
            # This is a simplified approach and may need to be expanded
            if hasattr(crawler_module, 'crawler'):
                crawler_module.crawler(comic_job.comic_url)
            else:
                logger.error(f"Unsupported crawler interface for {domain_pattern}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error crawling comic: {e}")
        return False