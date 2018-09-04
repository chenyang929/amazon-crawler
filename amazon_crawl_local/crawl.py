import asyncio
import copy
import queue
from config import Config
from crawl_func import clear_rds, start_crawl, start_thread
from store import AmazonRedis
from settings import REDIS_CONFIG_LOCAL


if __name__ == '__main__':

    que = queue.Queue()
    rds = AmazonRedis(Config.REDIS_NUM, **copy.deepcopy(REDIS_CONFIG_LOCAL))

    clear_rds(rds, Config)

    new_loop = asyncio.new_event_loop()

    start_thread(new_loop)

    try:
        while True:
            start_crawl(rds, que, Config, new_loop)
            # 队列都为空，采集完成
            if not rds.exists_key(Config.REDIS_START_URLS) and not rds.exists_key(Config.REDIS_REQUEST_URLS) and not rds.exists_key(Config.REDIS_CRAWL_URLS):
                break
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        new_loop.stop()



