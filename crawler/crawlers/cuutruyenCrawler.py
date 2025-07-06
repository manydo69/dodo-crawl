import time
import os
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from utils.img_utils import unscramble_from_json


# Load JavaScript code from file
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
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,3000")
    options.add_argument("--disable-features=PasteUnsanitizedContent")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Loading the target URL...")
    driver.get("https://cuutruyen.net")
    driver.execute_script("""
               localStorage.setItem("UIPreference3", "classic");
               localStorage.setItem("UIPreferenceConfirmed", "true");
           """)
    return driver


def crawler(url, js_code_to_inject):
    driver = setupDriver()

    print("Injecting JavaScript hook via CDP...")
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': js_code_to_inject}
    )

    driver.get(url)
    time.sleep(5)

    print("Injecting JavaScript hook...")
    driver.execute_script(js_code_to_inject)

    # Wait for the page to render and hook to collect data
    time.sleep(3)

    # Scroll the page slowly to ensure all images load
    print("Scrolling the page slowly to load all images...")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    scroll_step = 300  # Smaller step size for smoother scrolling

    while current_height < scroll_height:
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(0.4)  # Longer pause to ensure images load
        current_height += scroll_step
        # Update scroll height as content might be dynamically loaded
        scroll_height = driver.execute_script("return document.body.scrollHeight")

    # Retrieve the draw calls data
    draw_calls = driver.execute_script("return window.__drawCalls;")
    print(f"Collected {len(draw_calls)} draw calls")

    # You can process or save the draw calls data here,
    # For example, save it to a JSON file
    output_file = os.path.join(os.path.dirname(__file__), "canvas_draw_logs", "canvas_draw_calls.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(draw_calls, f, indent=2)

    print(f"Draw calls data saved to {output_file}")

    # Close the driver
    driver.quit()

    return draw_calls


if __name__ == "__main__":
    json_script = loadJsonScript()
    target_url = "https://cuutruyen.net/mangas/805/chapters/15784"
    crawler(target_url, json_script)
    json_path = "F:\myproject\dodo-crawl\crawler\canvas_draw_logs\canvas_draw_calls.json"
    save_folder = "F:\\myproject\\dodo-crawl\\results"
    unscramble_from_json(json_path, save_folder)
