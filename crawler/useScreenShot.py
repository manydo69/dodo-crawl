import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# ========== SETUP UNDETECTED CHROME ==========
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = uc.Chrome(options=options)
driver.implicitly_wait(10)

# ========== DOWNLOAD IMAGE BY SCREENSHOT ==========
def download_images_from_chapter(chapter_url, save_root="invincible"):
    print(f"🔗 Visiting: {chapter_url}")
    driver.get(chapter_url)
    time.sleep(6)  # wait for Cloudflare/JS

    if "Cloudflare" in driver.title or "blocked" in driver.page_source:
        print("❌ Blocked by Cloudflare.")
        return None

    chapter_name = chapter_url.strip("/").split("/")[-1]
    save_folder = os.path.join(save_root, chapter_name)
    os.makedirs(save_folder, exist_ok=True)

    image_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-images img")
    print(f"📸 Found {len(image_elements)} images")

    for i, img in enumerate(image_elements):
        try:
            file_path = os.path.join(save_folder, f"{i+1:02}.png")
            driver.execute_script("arguments[0].scrollIntoView(true);", img)
            time.sleep(0.5)  # ensure it's visible
            img.screenshot(file_path)
            print(f"✅ Screenshot saved: {file_path}")
        except Exception as e:
            print(f"❌ Failed to capture image {i+1}: {e}")

    print(f"✅ Completed chapter: {chapter_name}")

    # find "Issue sau" button
    try:
        next_button = driver.find_element(
            By.XPATH, '//a[@class="button primary is-small"][span[contains(text(),"Issue sau")]]'
        )
        return next_button.get_attribute("href")
    except:
        print("⛔ No next chapter found.")
        return None

# ========== MAIN LOOP ==========
start_url = "https://langgeek.net/invincible/chuong-1-50/"
current_url = start_url

while current_url:
    current_url = download_images_from_chapter(current_url)
    time.sleep(2)

driver.quit()
print("🎉 Done downloading all chapters.")
