import time
import os
import json
import sys
from tqdm import tqdm

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import unscramble_from_json
from s3_API import upload_folder_to_r2
from crawler import ComicCrawler


class CuutruyenComicCrawler(ComicCrawler):
    def __init__(self, base_dir="results"):
        super().__init__()
        self.comic_name = 'jojo_v7'  # Default comic name
        self.chapter_name = 'chapter_1'  # Default chapter name
        self.base_dir = base_dir  # Base directory for saving files

    def loadJsonScript(self):
        # Use a relative path that works on both Windows and Linux
        js_file_path = os.path.join(os.path.dirname(__file__), "hook_js", "hookDrawImage.js")
        print(f"JavaScript file path: {js_file_path}")
        print(f"File exists: {os.path.exists(js_file_path)}")
        with open(js_file_path, 'r', encoding='utf-8') as file:
            js_code_to_inject = file.read()
        print(f"JavaScript code length: {len(js_code_to_inject)}")
        return js_code_to_inject

    def set_up_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,3000")
        options.add_argument("--disable-features=PasteUnsanitizedContent")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Loading the target URL...")
        driver.get("https://cuutruyen.net")
        driver.execute_script("""
                       localStorage.setItem("UIPreference3", "classic");
                       localStorage.setItem("UIPreferenceConfirmed", "true");
                   """)
        return driver

    def crawl_page(self, driver, url):
        driver.get(url)
        time.sleep(3)

        canvas_count = driver.execute_script("return document.querySelectorAll('canvas').length;")
        print(f"🖼️ Total canvas elements: {canvas_count}")

        # Scroll the page slowly to ensure all images load
        print("Scrolling the page slowly to load all images...")
        scroll_step = 300  # Smaller step size for smoother scrolling
        draw_calls = []
        attempt_time = -1

        while len(draw_calls) == 0:
            attempt_time += 1
            current_height = 0
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            print(f"📏 Initial scroll height: {scroll_height}")

            pbar = tqdm(total=scroll_height, desc="Scrolling", unit="px")

            while current_height < scroll_height:
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                time.sleep(0.15)
                current_height += scroll_step
                scroll_height = driver.execute_script("return document.body.scrollHeight")
                pbar.total = scroll_height
                pbar.update(scroll_step)
            pbar.close()
            draw_calls = driver.execute_script("return window.__drawCalls;")
            print(f"Collected {len(draw_calls)} draw calls")
            if attempt_time > 5:
                time.sleep(10)
            else:
                time.sleep(1)

        # Save draw calls to a JSON file
        output_file = os.path.join(os.path.dirname(__file__), "canvas_draw_logs", "canvas_draw_calls.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(draw_calls, f, indent=2)

        print(f"Draw calls data saved to {output_file}")
        return draw_calls, output_file, canvas_count

    def crawl(self, url, comic_name=None, chapter_name=None):
        if comic_name:
            self.comic_name = comic_name
        if chapter_name:
            self.chapter_name = chapter_name

        # Load JavaScript and set up driver
        self.json_script = self.loadJsonScript()
        self.driver = self.set_up_driver()

        # Inject JavaScript hook
        print("Injecting JavaScript hook via CDP...")
        self.driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': self.json_script}
        )
        print("JavaScript hook injected successfully.")

        # Crawl the initial page
        _, output_file_path, number_canvas = self.crawl_page(self.driver, url)
        save_folder = os.path.join(self.base_dir, self.comic_name, self.chapter_name)
        image_get = unscramble_from_json(output_file_path, save_folder)
        print(f"Draw calls data: {image_get}/{number_canvas}")

        # Crawl subsequent chapters
        while True:
            try:
                next_button = self.driver.find_element(
                    By.XPATH,
                    "//a[.//span[@aria-label='Chevron Right icon']]"
                )
                next_href = next_button.get_attribute("href")
                print(f"➡️ Going to next chapter: {next_href}")
                self.chapter_name = self.chapter_name.split("_")[0] + "_" + str(int(self.chapter_name.split("_")[1]) + 1)
                _, output_file_path, number_canvas = self.crawl_page(self.driver, next_href)
                save_folder = os.path.join(self.base_dir, self.comic_name, self.chapter_name)
                image_get = unscramble_from_json(output_file_path, save_folder)
                print(f"Draw calls data: {image_get}/{number_canvas}")
                time.sleep(2)
            except Exception as e:
                print(f"✅ Reached last chapter or next button not found: {e}")
                break

        self.close()

    def web_code(self):
        return "CUUTRUYEN"


# Compatibility function for crawler_manager
def crawler(url, comic_name='jojo_v7', chapter_name='chapter_1', base_dir="results"):
    """
    Compatibility function for the crawler_manager.

    Args:
        url (str): URL to crawl
        comic_name (str, optional): Name of the comic. Defaults to 'jojo_v7'.
        chapter_name (str, optional): Name of the chapter. Defaults to 'chapter_1'.
        base_dir (str, optional): Base directory for saving files. Defaults to "results".
    """
    # Create and run the crawler instance
    crawler_instance = CuutruyenComicCrawler(base_dir=base_dir)
    crawler_instance.crawl(url, comic_name, chapter_name)

    # Upload the downloaded folder to R2 storage
    save_folder = str(os.path.join(base_dir, comic_name))
    try:
        print(f"☁️ Uploading folder to R2 storage from crawler function: {save_folder}")
        upload_success, upload_errors = upload_folder_to_r2(save_folder, f"comics/{comic_name}")
        print(f"☁️ Upload complete: {upload_success} files uploaded, {upload_errors} files failed")
    except Exception as e:
        print(f"❌ Error uploading folder to R2 from crawler function: {e}")


# For direct execution
if __name__ == "__main__":
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Cuutruyen Comic Crawler')
    parser.add_argument('--url', type=str, default="https://cuutruyen.net/mangas/805/chapters/65713",
                        help='URL to crawl')
    parser.add_argument('--comic', type=str, default='jojo_v7',
                        help='Name of the comic')
    parser.add_argument('--chapter', type=str, default='chapter_70',
                        help='Name of the chapter')

    args = parser.parse_args()

    target_url = args.url
    comic_name = args.comic
    chapter_name = args.chapter
    comic_dir = os.environ.get("COMIC_DIR")

    crawler(target_url, comic_name, chapter_name, comic_dir)
