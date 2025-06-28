from crawler.humanLikeCrawler import *


all_chapters = get_chapter_list()

for chapter_name, chapter_url in all_chapters:
    download_images_from_chapter(chapter_name, chapter_url)
    random_pause()

driver.quit()
print("🎉 All done.")