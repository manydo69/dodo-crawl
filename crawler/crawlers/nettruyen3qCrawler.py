import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==== CONFIG ====
url = ""  # Replace with real chapter URL
save_dir = "downloaded_images"
os.makedirs(save_dir, exist_ok=True)

# ==== SETUP SELENIUM ====
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

# ==== EXTRACT IMAGE URLS ====
image_elements = driver.find_elements(By.CSS_SELECTOR, "div.page-chapter img.lozad")
image_urls = []

for img in image_elements:
    data_src = img.get_attribute("data-src")
    if data_src:
        image_urls.append(data_src)

driver.quit()

# ==== DOWNLOAD IMAGES ====
for idx, img_url in enumerate(image_urls):
    try:
        response = requests.get(img_url, timeout=15)
        if response.status_code == 200:
            ext = img_url.split('?')[0].split('.')[-1]
            filename = f"{idx+1:03d}.{ext}"
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download {img_url}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")
