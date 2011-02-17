"redis-import-set"
import sys
from csv import reader
from itertools import groupby

import redis


def handle():
    #import pdb; pdb.set_trace()
    r = redis.Redis()
    print redis.__path__
    pipeline_redis = r.pipeline()

    count = 0
    try:
        keyname = sys.argv[1]
    except IndexError:
        raise Exception("You must specify the name for the Set")

    seen = set([None])
    for member, _ in groupby(reader(sys.stdin, delimiter='\t'),
    	                    lambda x:x[0] if len(x) else None):
        if member not in seen:
            pipeline_redis.sadd(keyname, member.rstrip())
            count += 1
            seen.add(member)
            if not count % 10000:
                pipeline_redis.execute()
    pipeline_redis.execute()


#if __name__ == '__main__':
    #handle()

