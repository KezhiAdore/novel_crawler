import re
import datetime
import requests
from lxml import etree
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


class NovelDownloader:
    """小说下载器，根据小说首页url下载整本小说返回为str
    并对其进行简单分析，得到总字数，章节数，平均单章字数
    等信息。
    """

    def __init__(self, client: requests.Session, encoding="utf-8") -> None:
        self._client = client
        self._novel = ""
        self._chapter_count = 0
        self._encoding = encoding
        self._metadata = {}

    def reset(self):
        self._novel = ""
        self._chapter_count = 0

    def get_novel(self, url) -> str:
        r = self._client.get(url)
        # 获取metadata
        print("开始解析小说主页{}".format(url))
        rp = etree.HTML(r.text)
        book = rp.xpath("//h1/text()")[0]   # 书名
        author = rp.xpath("//h1/small/a/text()")[0] # 作者
        category = rp.xpath("//div[@class='nav-mbx']/a[contains(@href,'fenlei')]/text()")   # 分类
        category = category[0] if category else None
        tag = rp.xpath("//p[@class='booktag']/span/text()")
        popularity = self._trans_popular(tag[0])    # 人气
        status = self._trans_status(tag[1]) # 状态
        update_info = rp.xpath("string(//div[@class='update'])")
        last_update_time = self._trans_update_time(update_info)
        self._metadata = {
            "book": self._valid_book(book),
            "author": author,
            "category": category,
            "popularity": popularity,
            "status": status,
            "last_update_time": last_update_time,
        }
        print("开始下载小说{}".format(book))
        
        self.download_novel(url)
        self._metadata["word_count"] = self.word_count()
        self._metadata["chapter_count"] = self.chapter_count()
        self._metadata["word_per_chapter"] = self.word_count()/self.chapter_count()
        print(self._metadata)
    
    def download_novel(self, url):
        # 解析目录，下载每一页文件
        chapter_urls = self.get_chapter_urls(url)
        self._chapter_count = len(chapter_urls)
        with ThreadPoolExecutor(128) as pool:
            results = pool.map(self.download_chapter,chapter_urls)
        self._novel = self._novel.join(results)
    
    def get_chapter_urls(self, url):
        print("正在解析目录{}".format(url))
        r = self._client.get(url)
        rp = etree.HTML(r.text)
        chapter_urls = rp.xpath("//dd/a/@href")
        chapter_urls = [urljoin(url, u) for u in chapter_urls]
        
        next_url = rp.xpath("//a[text()='下一页']/@href")
        if next_url:
            next_url = next_url[0]
        else:
            return chapter_urls
        
        if "/" not in next_url:
            return []
        else:
            next_url = urljoin(url, next_url)
            return chapter_urls + self.get_chapter_urls(next_url)
    
    def download_chapter(self,url):
        r = self._client.get(url)
        rp = etree.HTML(r.text)
        # 解析页面
        header = rp.xpath("//h1/text()")[0]
        content = rp.xpath("string(//div[@id='content'])")
        content = re.sub("笔趣阁(.+)章节！","",content) # 去除广告
        content = re.sub("\xa0+", "\n    ", content)    # 替换空白符
        print("{} 下载完毕".format(header))
        return '\n'+header+'\n'+content

    def metadata(self) -> dict:
        assert self._metadata, "获取Metadata前先调用函数`get_novel`获取小说"
        return self._metadata

    def word_count(self) -> int:
        assert self._novel, "获取全文字数前先调用函数`get_novel`获取小说"
        return len(self._novel)

    def chapter_count(self) -> int:
        assert self._chapter_count, "获取章节数前先调用函数`get_novel`获取小说"
        return self._chapter_count

    def save_novel(self, filepath):
        assert self._novel, "保存小说前先调用函数`get_novel`获取小说"
        with open(filepath, "w+", encoding=self._encoding) as f:
            f.write(self._novel)
            f.close()
    
    def _trans_popular(self, s:str) -> int:
        s = s.replace("人气：", "")
        if s.isdigit():
            return int(s)
        if "w+" in s:
            s = s.replace("w+", "")
            if s.isdigit():
                return int(s) * 10_000
        raise ValueError(s)
    
    def _trans_status(self, s:str) -> str:
        if "连载" in s:
            return "连载"
        if "完本" in s or "完成" in s:
            return "完本"
    
    def _trans_update_time(self, s:str) -> str:
        res = re.search("(?<=（)(.+)(?=）)",s[-19:])
        if not res:
            raise ValueError(s)
        s = res.group()
        tf = "%Y-%m-%d %H:%M"
        return datetime.datetime.strptime(s,tf)
    
    def _valid_book(self, s:str):
        for i, j in ("/／","\\＼","?？","|︱","\"＂","*＊","<＜",">＞"):
            s = s.replace(i,j)
        return s
