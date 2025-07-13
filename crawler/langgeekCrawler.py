import os
import time
import random
import zipfile

import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from crawler.ComicCrawler import ComicCrawler
from s3_API.api import upload_to_r2


class LanggeekCrawler(ComicCrawler):
    def __init__(self):
        super().__init__()
        self.comic_name = 'langgeek'  # Default comic name

        # Initialize cloudscraper
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

        # Setup Selenium
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(10)

    def zip_folder(self, folder_path):
        """
        Zip a folder.

        Args:
            folder_path (str): Path to the folder to zip

        Returns:
            str: Path to the zipped folder
        """
        zip_path = folder_path + ".zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, folder_path)
                    zipf.write(abs_path, rel_path)
        return zip_path

    def random_pause(self):
        """
        Pause for a random amount of time to simulate human behavior.
        """
        wait_time = random.uniform(0.1, 1)
        print(f"⏳ Waiting {wait_time:.1f} seconds like a human...")
        time.sleep(wait_time)

    def human_scroll(self):
        """
        Scroll the page in a human-like manner.
        """
        scroll_steps = random.randint(1, 3)
        for _ in range(scroll_steps):
            self.driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
            time.sleep(random.uniform(0.5, 1.5))

    def get_chapter_list(self, comic_url):
        """
        Get a list of all chapters from a comic page.

        Args:
            comic_url (str): URL of the comic page

        Returns:
            list: List of tuples (chapter_name, chapter_url)
        """
        self.driver.get(comic_url)
        time.sleep(5)

        select = Select(self.driver.find_element(By.CLASS_NAME, "change_issue_select"))
        chapters = []

        for option in select.options:
            url = option.get_attribute("value")
            name = option.text.strip().replace(" ", "_").replace("#", "")
            if url and url.startswith("http"):
                chapters.append((name, url))
        return chapters

    def download_images_from_chapter(self, chapter_name, chapter_url, save_root=None):
        """
        Download images from a chapter.

        Args:
            chapter_name (str): Name of the chapter
            chapter_url (str): URL of the chapter
            save_root (str, optional): Root folder to save images to. Defaults to self.comic_name.

        Returns:
            int: Number of successfully downloaded images
        """
        if save_root is None:
            save_root = self.comic_name

        print(f"🔗 Visiting: {chapter_url}")
        self.driver.get(chapter_url)
        self.human_scroll()

        if "Cloudflare" in self.driver.title or "Attention Required" in self.driver.page_source:
            print("❌ Bị Cloudflare chặn.")
            return 0

        save_folder = os.path.join(save_root, chapter_name)
        os.makedirs(save_folder, exist_ok=True)

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        image_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
        print(f"📸 Found {len(image_elements)} images")
        success_images = 0

        for i, img in enumerate(image_elements):
            img_url = (
                img.get_attribute("src")
                or img.get_attribute("alt")
                or img.get_attribute("data-src")
                or img.get_attribute("data-lazy-src")
            )
            if img_url and " " in img_url:
                img_url = img_url.split(" ")[0]

            if not img_url or not img_url.startswith("http"):
                print(f"⚠️ Skipped image {i+1}: invalid URL ({img_url})")
                continue

            try:
                img_data = self.scraper.get(img_url).content
                file_path = os.path.join(save_folder, f"{i+1:02}.jpg")
                with open(file_path, "wb") as f:
                    f.write(img_data)
                print(f"✅ Saved: {file_path}")
                success_images += 1
                time.sleep(random.uniform(0.2, 0.6))  # delay giữa ảnh
            except Exception as e:
                print(f"❌ Failed to download {img_url}: {e}")

        print(f"Success get {success_images}/{len(image_elements)} images")
        print(f"✅ Chapter done: {chapter_name}")
        return success_images

    def crawl(self, url, comic_name=None, chapter_name=None):
        """
        Crawl a comic and download all chapters.

        Args:
            url (str): URL of the comic page
            comic_name (str, optional): Name of the comic. Defaults to None.
            chapter_name (str, optional): Name of the chapter. Defaults to None.
        """
        if comic_name:
            self.comic_name = comic_name

        # Get all chapters
        all_chapters = self.get_chapter_list(url)
        print(f"📚 Found {len(all_chapters)} chapters")

        # Download images from each chapter
        for chapter_name, chapter_url in all_chapters:
            self.download_images_from_chapter(chapter_name, chapter_url, self.comic_name)
            self.random_pause()

        # Zip the comic folder
        comic_zip = self.zip_folder(self.comic_name)
        print(f"📦 Zipped comic folder: {comic_zip}")

        # Upload to R2 if available
        try:
            upload_to_r2(comic_zip, f"comics/{self.comic_name}.zip")
            print(f"☁️ Uploaded to R2: comics/{self.comic_name}.zip")
        except Exception as e:
            print(f"❌ Failed to upload to R2: {e}")

    def web_code(self):
        return "LANGGEEK"


# Compatibility functions for crawler_manager
def zip_folder(folder_path):
    """
    Compatibility function for the crawler_manager.

    Args:
        folder_path (str): Path to the folder to zip

    Returns:
        str: Path to the zipped folder
    """
    crawler_instance = LanggeekCrawler()
    return crawler_instance.zip_folder(folder_path)

def random_pause():
    """
    Compatibility function for the crawler_manager.
    """
    crawler_instance = LanggeekCrawler()
    crawler_instance.random_pause()

def get_chapter_list(comic_url):
    """
    Compatibility function for the crawler_manager.

    Args:
        comic_url (str): URL of the comic page

    Returns:
        list: List of tuples (chapter_name, chapter_url)
    """
    crawler_instance = LanggeekCrawler()
    return crawler_instance.get_chapter_list(comic_url)

def download_images_from_chapter(chapter_name, chapter_url, save_root):
    """
    Compatibility function for the crawler_manager.

    Args:
        chapter_name (str): Name of the chapter
        chapter_url (str): URL of the chapter
        save_root (str): Root folder to save images to

    Returns:
        int: Number of successfully downloaded images
    """
    crawler_instance = LanggeekCrawler()
    return crawler_instance.download_images_from_chapter(chapter_name, chapter_url, save_root)

def crawler(url, comic_name='langgeek', chapter_name=None):
    """
    Compatibility function for the crawler_manager.

    Args:
        url (str): URL to crawl
        comic_name (str, optional): Name of the comic. Defaults to 'langgeek'.
        chapter_name (str, optional): Name of the chapter. Defaults to None.
    """
    crawler_instance = LanggeekCrawler()
    crawler_instance.crawl(url, comic_name, chapter_name)
    crawler_instance.close()


# For direct execution
if __name__ == "__main__":
    target_url = "https://langgeek.net/invincible/"  # Replace with real comic URL
    comic_name = 'invincible'
    crawler(target_url, comic_name)
