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

from s3_API.api import upload_to_r2

scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

# ========= ZIP FOLDER =========
def zip_folder(folder_path):
    zip_path = folder_path + ".zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, folder_path)
                zipf.write(abs_path, rel_path)
    return zip_path

# ===== MÔ PHỎNG HÀNH VI NGƯỜI DÙNG =====
def random_pause():
    wait_time = random.uniform(2, 3)
    print(f"⏳ Waiting {wait_time:.1f} seconds like a human...")
    time.sleep(wait_time)

def human_scroll():
    scroll_steps = random.randint(3, 5)
    for _ in range(scroll_steps):
        driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
        time.sleep(random.uniform(0.5, 1.5))

# ===== LẤY DANH SÁCH TẤT CẢ CÁC CHƯƠNG TỪ DROPDOWN =====
def get_chapter_list():
    driver.get("https://langgeek.net/invincible/chuong-1-50/")
    time.sleep(5)

    select = Select(driver.find_element(By.CLASS_NAME, "change_issue_select"))
    chapters = []

    for option in select.options:
        url = option.get_attribute("value")
        name = option.text.strip().replace(" ", "_").replace("#", "")
        if url and url.startswith("http"):
            chapters.append((name, url))
    return chapters

# ===== TẢI ẢNH THEO CHƯƠNG =====
def download_images_from_chapter(chapter_name, chapter_url, save_root):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    human_scroll()

    if "Cloudflare" in driver.title or "Attention Required" in driver.page_source:
        print("❌ Bị Cloudflare chặn.")
        return

    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    image_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
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
            img_data = scraper.get(img_url).content
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


