import os
import time
import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Tạo session requests có bypass Cloudflare
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

# Cấu hình Selenium
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

# ========= Hàm tải ảnh theo src =========
def download_images_from_chapter(chapter_url, save_root="invincible"):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    time.sleep(6)

    if "Cloudflare" in driver.title or "Attention Required" in driver.page_source:
        print("❌ Bị Cloudflare chặn.")
        return None

    chapter_name = chapter_url.strip("/").split("/")[-1]
    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    # Scroll toàn trang để tải hết ảnh lazy-load
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
            img_url = img_url.split(" ")[0]  # Xử lý srcset

        if not img_url or not img_url.startswith("http"):
            print(f"⚠️ Skipped image {i+1}: invalid URL ({img_url})")
            continue

        try:
            img_data = scraper.get(img_url).content
            file_path = os.path.join(save_folder, f"{i+1:02}.jpg")
            with open(file_path, "wb") as f:
                f.write(img_data)
            print(f"✅ Saved: {file_path}")
        except Exception as e:
            print(f"❌ Failed to download {img_url}: {e}")

    print(f"✅ Chapter done: {chapter_name}")

    # Tìm nút "Issue sau"
    try:
        next_button = driver.find_element(
            By.XPATH, '//a[@class="button primary is-small"][span[contains(text(),"Issue sau")]]'
        )
        return next_button.get_attribute("href")
    except:
        print("⛔ No next chapter found.")
        return None

# ========= CHẠY =========
start_url = "https://langgeek.net/invincible/chuong-1-50/"
current_url = start_url

while current_url:
    current_url = download_images_from_chapter(current_url)
    time.sleep(2)

driver.quit()
print("🎉 Done!")
