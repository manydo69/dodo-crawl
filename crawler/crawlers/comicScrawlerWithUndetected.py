import os
import time
import requests
import urllib3
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Bỏ cảnh báo SSL nếu dùng verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== CẤU HÌNH TRÌNH DUYỆT (ẩn bot) =====
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# ===== KHỞI TẠO TRÌNH DUYỆT CHỐNG CLOUDLARE =====
driver = uc.Chrome(options=options)
driver.implicitly_wait(10)

# ===== TẢI ẢNH & CHUYỂN CHƯƠNG =====
def download_images_from_chapter(chapter_url, save_root="invincible"):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    time.sleep(6)  # Đợi JS + Cloudflare

    if "Cloudflare" in driver.title or "blocked" in driver.page_source:
        print("❌ Bị Cloudflare chặn.")
        return None

    # Tạo thư mục lưu ảnh
    chapter_name = chapter_url.strip("/").split("/")[-1]
    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    # Tìm ảnh trong div.list-images
    image_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
    print(f"📸 Found {len(image_elements)} images")

    for i, img in enumerate(image_elements):
        img_url = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("alt")
        if not img_url or not img_url.startswith("http"):
            print(f"⚠️ Skipped image at index {i}")
            continue

        try:
            img_data = requests.get(img_url, verify=False).content
            file_path = os.path.join(save_folder, f"{i+1:02}.jpg")
            with open(file_path, "wb") as f:
                f.write(img_data)
            print(f"✅ Saved: {file_path}")
        except Exception as e:
            print(f"❌ Failed to download image: {e}")

    print(f"✅ Completed chapter: {chapter_name}")

    # Tìm chương kế tiếp: nút "Issue sau"
    try:
        next_button = driver.find_element(
            By.XPATH, '//a[@class="button primary is-small"][span[contains(text(),"Issue sau")]]'
        )
        return next_button.get_attribute("href")
    except:
        print("⛔ Không còn chương tiếp theo.")
        return None

# ===== CHẠY CHÍNH =====
start_url = "https://langgeek.net/invincible/chuong-1-50/"  # ✅ THAY ĐỔI nếu cần
current_url = start_url

while current_url:
    current_url = download_images_from_chapter(current_url)
    time.sleep(2)

driver.quit()
print("🎉 Xong hết rồi!")
