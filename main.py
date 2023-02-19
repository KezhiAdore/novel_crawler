from crawler import *
import pandas as pd
import os

base_url = "https://www.bbiquge.net/book/"
data_dir = "C:/Users/kezhi/Desktop/data"
novel_dir = os.path.join(data_dir, "novel")
novel_data_file = os.path.join(data_dir, "novel_data.csv")
columns = [
    "id",
    "book",
    "author",
    "category",
    "popularity",
    "status",
    "last_update_time",
    "word_count",
    "chapter_count",
    "word_per_chapter",
    "novel_filepath",
]


novel_dl = NovelDownloader(client)

def init():
    # 检查目录和文件的存在情况
    if not os.path.exists(novel_dir):
        os.makedirs(novel_dir)
    if not os.path.exists(novel_data_file):
        df = pd.DataFrame(columns=columns)
        df.to_csv(novel_data_file)
    print("初始化完成")

# 初始化
init()

# 由于整个笔趣阁数据库很大，爬取过程中发生中断很正常,需要做好中断重爬的工作。

# 加载爬取进度
df = pd.read_csv(novel_data_file,index_col=0)

# 根据笔趣阁书的编号逐一遍历并保存
for book_id in range(10000):
    # 重置小说下载器
    novel_dl.reset()
    # 构建小说页面链接
    book_url = os.path.join(base_url, str(book_id)+'/')
    # 检查是否已经爬过信息
    if book_id in df.index:
        # 检查小说全文是否已下载
        novel_filepath = df.loc[book_id, "novel_filepath"]
        if not os.path.exists(novel_filepath):
            novel_dl.get_novel(book_url)
            novel_dl.save_novel(novel_filepath)
        continue
    
    # 尝试获取小说页面
    r = client.get(book_url)
    # 判断页面是否合法
    if "出现错误" in r.text:
        print("id为{}的小说不存在".format(book_id))
        continue
    
    # 获取小说元信息
    novel_dl.get_novel(book_url)
    novel_filepath = df.loc[book_id, "novel_filepath"]
    novel_dl.save_novel(novel_filepath)
    novel_info = novel_dl.metadata()
    novel_info["id"] = book_id
    novel_info["novel_filepath"] = novel_filepath
    
    print(novel_info)
    
    info_row = pd.DataFrame(novel_info)
    df = pd.concat([df, info_row])
    df.to_csv(novel_data_file)