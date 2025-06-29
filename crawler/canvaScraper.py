import os
import base64
import hashlib
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def setup_driver():
    options = Options()
    # options.add_argument("--headless=new")  # optional
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,3000")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://cuutruyen.net")
    driver.execute_script("""
        localStorage.setItem("UIPreference3", "classic");
        localStorage.setItem("UIPreferenceConfirmed", "true");
    """)
    return driver


def capture_canvas_if_unique(canvas, idx, save_path, hash_set, driver):
    try:
        data_url = driver.execute_script(
            "return arguments[0].toDataURL('image/jpeg', 1.0);", canvas
        )

        data_url2 = driver.execute_script(
            "return arguments[0].toDataURL('image/png', 1.0);", canvas
        )

        if not data_url.startswith("data:image/jpeg;base64,"):
            print(f"⚠️ Invalid data URL for canvas {idx}")
            return False

        img_data = base64.b64decode(data_url.split(",")[1])
        with open(save_path / f"{idx:03}.jpg", "wb") as f:
            f.write(img_data)
        print(f"✅ Saved page {idx:03}.jpg")
        return True
    except Exception as e:
        print(f"❌ Error on canvas {idx}: {e}")
        return False


def extract_canvas_images(url: str, save_dir: str):
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)

    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    while current_height < scroll_height:
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.1)
        current_height += 500
        scroll_height = driver.execute_script("return document.body.scrollHeight")

    time.sleep(2)
    canvases_count = len(driver.find_elements(By.TAG_NAME, "canvas"))
    print(f"🎯 Found {canvases_count} canvases")

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    hash_set = set()
    for idx in range(canvases_count):
        try:
            canvas = driver.find_elements(By.TAG_NAME, "canvas")[idx]  # Re-fetch fresh
            capture_canvas_if_unique(canvas, idx + 1, save_path, hash_set, driver)
        except Exception as e:
            print(f"❌ Failed to fetch canvas {idx + 1}: {e}")

    driver.quit()
    print("🎉 Done.")


# Example usage
if __name__ == "__main__":
    extract_canvas_images(
        "https://cuutruyen.net/mangas/805/chapters/15784",
        "comics/805/15784"
    )
