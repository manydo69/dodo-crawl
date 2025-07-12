class ComicCrawler:
    def __init__(self):
        self.driver = None
        self.url = None
        self.data = None
        self.json_script = None

    def crawl(self, url):
        pass

    def crawl_all(self, urls):
        pass

    def save(self, data):
        pass

    def save_all(self, datas):
        pass

    def close(self):
        self.driver.quit()

    def web_code(self):
        pass
