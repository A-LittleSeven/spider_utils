import requests
import logging
import traceback
import json
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


class Wallpaper(object):

    OBJ_URL = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n={offset}&pid=hp&video={includeVideo}"
    BASE_URL = "https://cn.bing.com"
    UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61'}

    def __init__(self, offset=8, includeVideo=1):
        self.offset = offset
        self.includeVideo = includeVideo

    def __call__(self):
        self.crawl()

    def _subcrawl(self, item: dict):
        pic_link = self.BASE_URL + item["url"]
        title = item["copyright"].split("(")[0]
        res = requests.get(pic_link, headers=self.UA)
        with open(title + ".jpg", "wb") as fp:
            fp.write(res.content)
        return 'ok'
    
    def crawl(self):
        try:
            res = requests.get(self.OBJ_URL.format(offset=self.offset, includeVideo=self.includeVideo), headers=self.UA)
            js = json.loads(res.text)  # type: dict
            js_images = js["images"]
            # 多线程抓取
            with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count(), thread_name_prefix="bingWallPaper_") as executor:
                futures = [executor.submit(self._subcrawl, item)
                           for item in js_images]
                res = [f.result() for f in futures]
            print(res)
        except requests.exceptions.ConnectionError as e:
            logging.info(traceback.format_exc())

if __name__ == "__main__":
    s = Wallpaper(8, 1)
