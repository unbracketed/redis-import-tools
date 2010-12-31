"redis-import-set"
import sys

import redis


def handle():
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    try:
        keyname = sys.argv[1]
    except IndexError:
        raise Exception("You must specify the name for the Set")

    for line in sys.stdin:
        pipeline_redis.sadd(keyname, line.rstrip())
        count += 1
        if not count % 10000:
            pipeline_redis.execute()
    pipeline_redis.execute()


if __name__ == '__main__':
    handle()

