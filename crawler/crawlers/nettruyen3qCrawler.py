import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from crawler.ComicCrawler import ComicCrawler
from s3_API.api import upload_folder_to_r2


class Nettruyen3qCrawler(ComicCrawler):
    def __init__(self):
        super().__init__()
        self.comic_name = 'nettruyen'  # Default comic name

        # ==== SETUP SELENIUM ====
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless=new")  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def extract_image_urls(self, chapter_url):
        """
        Extract image URLs from a chapter page.

        Args:
            chapter_url (str): URL of the chapter page

        Returns:
            list: List of image URLs
        """
        print(f"🔗 Visiting: {chapter_url}")
        self.driver.get(chapter_url)
        time.sleep(3)  # Wait for page to load

        image_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.page-chapter img.lozad")
        image_urls = []

        for img in image_elements:
            data_src = img.get_attribute("data-src")
            if data_src:
                image_urls.append(data_src)

        print(f"📸 Found {len(image_urls)} images")
        return image_urls

    def download_images(self, image_urls, save_folder):
        """
        Download images from URLs.

        Args:
            image_urls (list): List of image URLs
            save_folder (str): Folder to save images to

        Returns:
            int: Number of successfully downloaded images
        """
        os.makedirs(save_folder, exist_ok=True)
        success_count = 0

        for idx, img_url in enumerate(image_urls):
            try:
                response = requests.get(img_url, timeout=15)
                if response.status_code == 200:
                    ext = img_url.split('?')[0].split('.')[-1]
                    if not ext or len(ext) > 4:  # If extension is invalid or missing
                        ext = "jpg"
                    filename = f"{idx+1:03d}.{ext}"
                    file_path = os.path.join(save_folder, filename)

                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Downloaded: {filename}")
                    success_count += 1
                else:
                    print(f"❌ Failed to download {img_url}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Error downloading {img_url}: {e}")

        return success_count

    def crawl(self, url, comic_name=None, chapter_name=None):
        """
        Crawl a chapter and download images.

        Args:
            url (str): URL of the chapter page
            comic_name (str, optional): Name of the comic. Defaults to None.
            chapter_name (str, optional): Name of the chapter. Defaults to None.
        """
        if comic_name:
            self.comic_name = comic_name

        # Extract chapter name from URL if not provided
        if not chapter_name:
            chapter_name = url.strip("/").split("/")[-1]
            if not chapter_name:
                chapter_name = "chapter_1"

        # Create save folder
        save_folder = os.path.join(self.comic_name, chapter_name)

        # Extract image URLs and download images
        image_urls = self.extract_image_urls(url)
        success_count = self.download_images(image_urls, save_folder)

        print(f"✅ Completed chapter: {chapter_name} ({success_count}/{len(image_urls)} images)")

        # Upload the downloaded folder to R2 storage
        try:
            print(f"☁️ Uploading folder to R2 storage: {save_folder}")
            upload_success, upload_errors = upload_folder_to_r2(save_folder, f"{self.comic_name}/{chapter_name}")
            print(f"☁️ Upload complete: {upload_success} files uploaded, {upload_errors} files failed")
        except Exception as e:
            print(f"❌ Error uploading folder to R2: {e}")

    def web_code(self):
        return "NETTRUYEN3Q"


# Compatibility function for crawler_manager
def crawler(url, comic_name='nettruyen', chapter_name=None):
    """
    Compatibility function for the crawler_manager.

    Args:
        url (str): URL to crawl
        comic_name (str, optional): Name of the comic. Defaults to 'nettruyen'.
        chapter_name (str, optional): Name of the chapter. Defaults to None.
    """
    crawler_instance = Nettruyen3qCrawler()
    crawler_instance.crawl(url, comic_name, chapter_name)
    crawler_instance.close()


# For direct execution
if __name__ == "__main__":
    target_url = "https://nettruyen3q.com/truyen-tranh/chapter-url"  # Replace with real chapter URL
    comic_name = 'nettruyen'
    crawler(target_url, comic_name)
