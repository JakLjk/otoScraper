from redis import Redis
from rq import Worker, Queue
from config import APPCONFIG

redis_conn = Redis.from_url(APPCONFIG.REDIS_URL)
queue = Queue(connection=redis_conn)

if __name__ == '__main__':
    worker = Worker([queue], connection=redis_conn)
    worker.work()