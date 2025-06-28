import os
import time
import random
import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# ===== TẠO CLOUDSCRAPER BỎ QUA CLOUDFLARE =====
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

# ===== CẤU HÌNH CHROME =====
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

# ===== MÔ PHỎNG HÀNH VI NGƯỜI DÙNG =====
def random_pause():
    wait_time = random.uniform(4, 9)
    print(f"⏳ Waiting {wait_time:.1f} seconds like a human...")
    time.sleep(wait_time)

def human_scroll():
    scroll_steps = random.randint(3, 6)
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
def download_images_from_chapter(chapter_name, chapter_url, save_root="invincible"):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    time.sleep(random.uniform(5, 8))
    human_scroll()

    if "Cloudflare" in driver.title or "Attention Required" in driver.page_source:
        print("❌ Bị Cloudflare chặn.")
        return

    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    image_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
    print(f"📸 Found {len(image_elements)} images")

    for i, img in enumerate(image_elements):
        img_url = (
            img.get_attribute("src")
            or img.get_attribute("data-src")
            or img.get_attribute("data-lazy-src")
            or img.get_attribute("alt")
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
            time.sleep(random.uniform(0.2, 0.6))  # delay giữa ảnh
        except Exception as e:
            print(f"❌ Failed to download {img_url}: {e}")

    print(f"✅ Chapter done: {chapter_name}")

# ===== MAIN =====
all_chapters = get_chapter_list()

for chapter_name, chapter_url in all_chapters:
    download_images_from_chapter(chapter_name, chapter_url)
    random_pause()

driver.quit()
print("🎉 All done.")
