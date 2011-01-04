"redis-import-set"
import sys
from csv import reader
from itertools import groupby

from gevent import monkey; monkey.patch_socket()
import gevent
import redis


def handle(**kwargs):
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    key = kwargs['key']
    
    seen = set([None])
    for member, _ in groupby(reader(sys.stdin, delimiter='\t'),
    	                    lambda x:x[0] if len(x) else None):
        if member not in seen:
            pipeline_redis.sadd(key, member.rstrip())
            count += 1
            seen.add(member)
            if not count % 10000:
                gevent.spawn(pipeline_redis.execute).join()
    pipeline_redis.execute()


if __name__ == '__main__':
    handle(**options)


