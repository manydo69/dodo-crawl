import json
import os
from PIL import Image
from io import BytesIO
import cloudscraper

class ScrambledImage:
    def __init__(self, img_url, index):
        self.width = 0
        self.height = 0
        self.img = None
        self.segments = []
        self.img_idx = index
        self.img_url = img_url
        self.processed_segments = set()

    def add_segment(self, sx, sy, s_width, s_height, dx, dy, d_width, d_height):
        segment_signature = (sx, sy, s_width, s_height, dx, dy, d_width, d_height)
        if segment_signature in self.processed_segments:
            return

        self.processed_segments.add(segment_signature)

        source_box = (sx, sy, sx + s_width, sy + s_height)
        dest_coords = (dx, dy)
        dest_size = (d_width, d_height)
        self.segments.append((source_box, dest_coords, dest_size))
        self.width = max(self.width, dx + d_width)
        self.height = self.height + d_height

    def download_image(self, scraper):
        """Downloads the source image using a cloudscraper session."""
        if self.img is None:
            try:
                res = scraper.get(self.img_url, timeout=20)
                res.raise_for_status()  # Raise an exception for bad status codes
                self.img = Image.open(BytesIO(res.content)).convert("RGB")
            except cloudscraper.exceptions.CloudflareException as e:
                print(f"Cloudflare challenge failed for {self.img_url}: {e}")
            except Exception as e:
                print(f"Failed to download {self.img_url}: {e}")

    def unscramble(self):
        if not self.img:
            print(f"Cannot unscramble, image not downloaded for {self.img_url}")
            return None
        canvas = Image.new("RGB", (self.width, self.height), (255, 255, 255))

        for source_box, dest_coords, dest_size in self.segments:
            segment = self.img.crop(source_box)
            if segment.size != dest_size:
                segment = segment.resize(dest_size)
            canvas.paste(segment, dest_coords)

        return canvas


def unscramble_from_json(json_path, folder_path="results"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            draw_calls = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file {json_path}: {e}")
        return

    index = 0
    image_data_map = {}
    for idx, call in enumerate(draw_calls):
        try:
            src = call["src"]
            if src not in image_data_map:
                index += 1
                image_data_map[src] = ScrambledImage(src, index)

            image_data_map[src].add_segment(
                sx=call["sx"],
                sy=call["sy"],
                s_width=call["sWidth"],
                s_height=call["sHeight"],
                dx=call["dx"],
                dy=call["dy"],
                d_width=call["dWidth"],
                d_height=call["dHeight"]
            )

        except Exception as e:
            print(f"Lỗi ở tile {idx}: {e}")

    scraper = cloudscraper.create_scraper()
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for url, image_data in image_data_map.items():
        image_data.download_image(scraper)
        final_image = image_data.unscramble()
        if final_image:
            save_path = f"result_{image_data.img_idx}.jpg"
            final_image.save(os.path.join(folder_path, save_path))
            print(f"Successfully saved: {save_path}")

    return len(image_data_map)

if __name__ == '__main__':
    json_path = "F:\myproject\dodo-crawl\crawler\canvas_draw_logs\canvas_draw_calls.json"
    save_folder = "F:\\myproject\\dodo-crawl\\results"
    unscramble_from_json(json_path, save_folder)
