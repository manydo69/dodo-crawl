import time
import os
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from utils.img_utils import unscramble_from_json


def loadJsonScript():
    js_file_path = "F:\\myproject\\dodo-crawl\\crawler\\hook_js\\hookDrawImage.js"
    print(f"JavaScript file path: {js_file_path}")
    print(f"File exists: {os.path.exists(js_file_path)}")
    with open(js_file_path, 'r', encoding='utf-8') as file:
        js_code_to_inject = file.read()
    print(f"JavaScript code length: {len(js_code_to_inject)}")
    return js_code_to_inject


def setupDriver():
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


def crawler(driver, url):
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

    # For example, save it to a JSON file
    output_file = os.path.join(os.path.dirname(__file__), "canvas_draw_logs", "canvas_draw_calls.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(draw_calls, f, indent=2)

    print(f"Draw calls data saved to {output_file}")
    return draw_calls, output_file, canvas_count


if __name__ == "__main__":
    next_chapter = ''
    json_script = loadJsonScript()
    comic_name = 'jojo_v7'
    driver = setupDriver()

    print("Injecting JavaScript hook via CDP...")
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': json_script}
    )
    print("JavaScript hook injected successfully.")
    chapter_name = 'chapter_16'
    target_url = "https://cuutruyen.net/mangas/805/chapters/24803"
    _, output_file_path, number_canvas = crawler(driver, target_url)
    save_folder = "F:\\myproject\\dodo-crawl\\results\\" + comic_name + "\\" + chapter_name
    image_get = unscramble_from_json(output_file_path, save_folder)
    print(f"Draw calls data: {image_get}/{number_canvas}")

    while True:
        try:
            next_button = driver.find_element(
                By.XPATH,
                "//a[.//span[@aria-label='Chevron Right icon']]"
            )
            next_href = next_button.get_attribute("href")
            print(f"➡️ Going to next chapter: {next_href}")
            chapter_name = chapter_name.split("_")[0] + "_" + str(int(chapter_name.split("_")[1]) + 1)
            _, output_file_path, number_canvas = crawler(driver, next_href)
            save_folder = "F:\\myproject\\dodo-crawl\\results\\" + comic_name + "\\" + chapter_name
            image_get = unscramble_from_json(output_file_path, save_folder)
            print(f"Draw calls data: {image_get}/{number_canvas}")

            time.sleep(2)
        except:
            print("✅ Reached last chapter or next button not found.")
            break

    driver.quit()
