import shutil

from crawler.humanLikeCrawler import *

comic = "invincible"
all_chapters = get_chapter_list()

for chapter_name, chapter_url in all_chapters:
    download_images_from_chapter(chapter_name, chapter_url, save_root=comic)
    random_pause()

# 🔒 Zip full comic folder
comic_zip = f"{comic}.zip"
shutil.make_archive(comic, 'zip', root_dir=comic)
print(f"📦 Zipped: {comic_zip}")

# 📤 Upload to R2
upload_to_r2(comic_zip, f"comics/{comic}.zip")
print(f"✅ Uploaded: comics/{comic}.zip")

# 🧹 Optional cleanup
os.remove(comic_zip)
shutil.rmtree(comic)

driver.quit()
print("🎉 All done.")