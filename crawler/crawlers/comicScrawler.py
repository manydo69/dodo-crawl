import os
import time
import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Tắt cảnh báo SSL (vì dùng verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== SETUP TRÌNH DUYỆT CHROME GIỐNG NGƯỜI DÙNG THẬT =====
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# KHÔNG headless trong lần chạy đầu (Cloudflare cần JS + cookie)
# options.add_argument("--headless")  # Bật sau khi đã vào thành công nếu muốn

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ===== TẢI ẢNH VÀ TÌM LINK ISSUE SAU =====
def download_images_from_chapter(chapter_url, save_root="invincible"):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    time.sleep(8)  # Đợi JS & Cloudflare xử lý

    # Phát hiện bị chặn bởi Cloudflare
    if "Cloudflare" in driver.title or "blocked" in driver.page_source:
        print("⛔ Bị chặn bởi Cloudflare, hãy thử đổi IP hoặc đợi vài phút.")
        return None

    # Tạo thư mục lưu ảnh
    chapter_name = chapter_url.strip("/").split("/")[-1]
    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    # Tìm ảnh trong div.list-images
    image_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
    print(f"📸 Found {len(image_elements)} images in {chapter_name}")

    for i, img in enumerate(image_elements):
        img_url = img.get_attribute("src")
        if not img_url or not img_url.startswith("http"):
            img_url = img.get_attribute("data-src") or img.get_attribute("alt")
        if not img_url or not img_url.startswith("http"):
            print(f"⚠️ Skipped invalid image at index {i}")
            continue

        try:
            img_data = requests.get(img_url, verify=False).content
            file_path = os.path.join(save_folder, f"{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(img_data)
            print(f"✅ Saved: {file_path}")
        except Exception as e:
            print(f"❌ Error downloading {img_url}: {e}")

    print(f"✅ Completed chapter: {chapter_name}")

    # Tìm nút "Issue sau"
    try:
        next_button = driver.find_element(
            By.XPATH, '//a[@class="button primary is-small"][span[contains(text(),"Issue sau")]]'
        )
        next_href = next_button.get_attribute("href")
        return next_href
    except:
        print("⛔ Không tìm thấy nút 'Issue sau'. Kết thúc.")
        return None

# ===== CHẠY TOÀN BỘ CHƯƠNG =====
start_url = "https://langgeek.net/invincible/chuong-1-50/"  # thay đổi nếu cần
current_url = start_url

while current_url:
    current_url = download_images_from_chapter(current_url)
    time.sleep(2)  # nghỉ giữa các chapter để tránh bị block tiếp

driver.quit()
print("🎉 Tải xong toàn bộ.")
