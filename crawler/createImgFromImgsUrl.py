# Đây là file tạm thời sắp lại 1 ảnh hoàn chỉnh.
# trong file json, nó không chỉ chứa 14 ảnh bị cắt mà còn chứa rất nhiều phần tử ảnh bị cắt khác
# Map theo src -> mỗi entry lúc này tương ứng với 1 ảnh (value sẽ gồm VD 14 phần tử của ảnh đã bị cắt)
# Tối ưu lại chỗ này để chạy được 1 lúc nhiều file nhé, nên nhớ là khi map thì nên map theo thứ tự
# Để các ảnh sau khi ghép lại cx theo thứ tự
# Nhờ a Phúc refactor lại ạ rồi merge vào dev -> stg -> master

import json
import os
from PIL import Image
from io import BytesIO
import cloudscraper

# Tạo thư mục chứa tile nếu chưa có
os.makedirs("canvas_tiles", exist_ok=True)
# 
pathImgsUrl = '... path lưu file json chứa bộ nguồn ảnh cùng tọa độ'
with open(pathImgsUrl, "r", encoding="utf-8") as f:
    draw_calls = json.load(f)

# Khởi tạo cloudscraper session để vượt Cloudflare
scraper = cloudscraper.create_scraper()

# Tính kích thước ảnh tổng
max_width = max(call["dx"] + call["dWidth"] for call in draw_calls)
max_height = max(call["dy"] + call["dHeight"] for call in draw_calls)

# Tạo canvas trống
canvas = Image.new("RGB", (max_width, max_height), (255, 255, 255))

# Lặp qua từng tile để tải và dán
for idx, call in enumerate(draw_calls):
    try:
        src = call["src"]
        print(f"[{idx+1}/{len(draw_calls)}] Tải: {src}")

        filename = os.path.join("canvas_tiles", f"tile_{idx}.jpg")

        if not os.path.exists(filename):
            res = scraper.get(src, timeout=15)
            img = Image.open(BytesIO(res.content)).convert("RGB")
            img.save(filename)
        else:
            img = Image.open(filename).convert("RGB")

        # Cắt vùng từ ảnh gốc
        tile = img.crop((
            call["sx"],
            call["sy"],
            call["sx"] + call["sWidth"],
            call["sy"] + call["sHeight"]
        ))

        # Resize nếu cần
        if (call["sWidth"], call["sHeight"]) != (call["dWidth"], call["dHeight"]):
            tile = tile.resize((call["dWidth"], call["dHeight"]))

        # Dán vào canvas
        canvas.paste(tile, (call["dx"], call["dy"]))

    except Exception as e:
        print(f"Lỗi ở tile {idx}: {e}")

# Lưu kết quả
canvas.save("result.jpg")
print("Ảnh đã được lưu vào result.jpg")