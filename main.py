import shutil

from crawler.humanLikeCrawler import *
from utils.slugify import slugify

comic_folder = "dark-nights-metal"
comic_url = "https://langgeek.net/dark-nights-metal/1-dark-days-the-forge/"
all_chapters = get_chapter_list(comic_url)

for chapter_name, chapter_url in all_chapters[9:]:
    download_images_from_chapter(slugify(chapter_name), chapter_url, save_root=comic_folder)
    random_pause()

# 🔒 Zip full comic folder
comic_zip = f"{comic_folder}.zip"
shutil.make_archive(comic_folder, 'zip', root_dir=comic_folder)
print(f"📦 Zipped: {comic_zip}")

# 📤 Upload to R2
upload_to_r2(comic_zip, f"comics/{comic_folder}.zip")
print(f"✅ Uploaded: comics/{comic_folder}.zip")

driver.quit()
print("🎉 All done.")