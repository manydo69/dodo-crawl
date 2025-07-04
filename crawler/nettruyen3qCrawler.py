import os
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==== CONFIG ====
url = "https://nettruyen3q.com/read/toi-thang-cap-mot-minh-ss2/vn/chapter-1"  # Replace with real chapter URL
save_dir = "comics/downloaded_images"
os.makedirs(save_dir, exist_ok=True)

# ==== SETUP SELENIUM ====
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)
time.sleep(10)

scroll_height = driver.execute_script("return document.body.scrollHeight")
current_height = 0
while current_height < scroll_height:
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(0.5)
    current_height += 500
    scroll_height = driver.execute_script("return document.body.scrollHeight")

# ==== EXTRACT IMAGE URLS ====
image_elements = driver.find_elements(By.CSS_SELECTOR, "div.page-chapter img.lozad")
image_urls = []

for img in image_elements:
    data_src = img.get_attribute("src")
    if data_src:
        image_urls.append(data_src)

driver.quit()

# ==== DOWNLOAD IMAGES ====
#'https://h2.nettruyen3q.net/storage/file/tt?data=9151c64a934be41ac94ea2f4d4a38c61f0ca8011fb644c17260dcfb81eb84579a8d8878ab0dd1a3cc42cd242b051a570&host=gg'
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
