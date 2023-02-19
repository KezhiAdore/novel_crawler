import requests
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


SLEEP_INTERVAL = 0.1 # sleep time between retries
MAX_RETRIES = 10 # Number of times to retry a request

USE_PROXY=False # whether use proxy globally

# setting http proxy globally
if USE_PROXY:
    os.environ["http_proxy"]="http://127.0.0.1:10809"
    os.environ["https_proxy"]="http://127.0.0.1:10809"

retries=Retry(
    total=MAX_RETRIES,
    backoff_factor=SLEEP_INTERVAL,
    status_forcelist=[403, 500, 502, 503, 504],
)

default_headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62",
    "Accept-Encoding": "gzip, deflate",
}

client = requests.Session()
client.mount("http://", HTTPAdapter(max_retries=retries))
client.mount("https://", HTTPAdapter(max_retries=retries))
client.headers=default_headers