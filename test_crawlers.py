import os
import sys
from crawler.crawler_manager import crawl_comic

# Define a simple class to mimic ComicJobDetail
class ComicJobDetail:
    def __init__(self, comic_url, comic_folder_name):
        self.comic_url = comic_url
        self.comic_folder_name = comic_folder_name

def test_crawler(url, folder_name):
    print(f"Testing crawler for URL: {url}")
    job = ComicJobDetail(url, folder_name)
    success = crawl_comic(job)
    print(f"Crawler {'succeeded' if success else 'failed'} for {url}")
    return success

if __name__ == "__main__":
    # Test each crawler with a sample URL
    test_cases = [
        # Uncomment the test cases you want to run
        # ("https://cuutruyen.net/mangas/805/chapters/30899", "jojo_test"),
        # ("https://langgeek.net/invincible/", "invincible_test"),
        # ("https://nettruyen3q.com/truyen-tranh/chapter-url", "nettruyen_test"),
    ]
    
    # Run the selected test cases
    for url, folder_name in test_cases:
        test_crawler(url, folder_name)
        print("-" * 50)