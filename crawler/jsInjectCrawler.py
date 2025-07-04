import os
import time
import base64
import requests
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ========== JavaScript to inject drawImage hook ==========
HOOK_JS = """
(() => {
    const original = CanvasRenderingContext2D.prototype.drawImage;
    const logs = [];

    CanvasRenderingContext2D.prototype.drawImage = function(...args) {
        try {
            const img = args[0];

            if (img && img.src) {
                if (args.length === 3) {
                    logs.push({ src: img.src, x: args[1], y: args[2] });
                } else if (args.length === 5) {
                    logs.push({ src: img.src, x: args[1], y: args[2], w: args[3], h: args[4] });
                } else if (args.length === 9) {
                    logs.push({
                        src: img.src,
                        sx: args[1], sy: args[2],
                        sWidth: args[3], sHeight: args[4],
                        dx: args[5], dy: args[6],
                        dWidth: args[7], dHeight: args[8],
                    });
                }
            }
        } catch (err) {
            console.error("drawImage hook error:", err);
        }

        return original.apply(this, args);
    };

    window.__drawCalls = logs;
    console.log("drawImage hook installed.");
})();
"""

def setup_driver():
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,3000")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver

def reconstruct_image(draw_calls, save_path):
    if not draw_calls:
        print("No draw calls found.")
        return

    # Determine canvas size
    max_x = max(call.get("dx", call.get("x", 0)) + call.get("dWidth", call.get("w", 0)) for call in draw_calls)
    max_y = max(call.get("dy", call.get("y", 0)) + call.get("dHeight", call.get("h", 0)) for call in draw_calls)
    final_img = Image.new("RGB", (max_x, max_y), "white")

    for i, call in enumerate(draw_calls):
        try:
            img_url = call["src"]
            response = requests.get(img_url, timeout=10)
            tile = Image.open(BytesIO(response.content)).convert("RGB")

            # Resize if needed
            if "dWidth" in call and "dHeight" in call:
                tile = tile.resize((call["dWidth"], call["dHeight"]))

            final_img.paste(tile, (call.get("dx", call.get("x", 0)), call.get("dy", call.get("y", 0))))
        except Exception as e:
            print(f"❌ Failed to paste tile {i}: {e}")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    final_img.save(save_path)
    print(f"✅ Saved reconstructed image to {save_path}")

def scrape_chapter(url, save_path):
    driver = setup_driver()
    driver.get(url)
    driver.execute_script("""
                localStorage.setItem("UIPreference3", "classic");
                localStorage.setItem("UIPreferenceConfirmed", "true");
            """)
    time.sleep(3)

    # Inject hook and scroll to trigger rendering
    driver.execute_script(HOOK_JS)
    for _ in range(150):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.1)

    time.sleep(2)  # wait for full render
    draw_calls = driver.execute_script("return window.__drawCalls;")
    driver.quit()

    reconstruct_image(draw_calls, save_path)

if __name__ == "__main__":
    comic_url = "https://cuutruyen.net/mangas/805/chapters/15784"
    save_to = "output/reconstructed.jpg"
    scrape_chapter(comic_url, save_to)
