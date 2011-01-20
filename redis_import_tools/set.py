"redis-import-set"
import sys
from csv import reader
from itertools import groupby

import redis


def handle(**kwargs):
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    key = kwargs['key']
    batch_size = kwargs['batch_size']
    
    seen = set([None])
    for member, _ in groupby(reader(sys.stdin, delimiter='\t'),
    	                    lambda x:x[0] if len(x) else None):
        if member not in seen:
            pipeline_redis.sadd(key, member.rstrip())
            count += 1
            seen.add(member)
            if not count % batch_size:
                pipeline_redis.execute()
    #send the last batch
    pipeline_redis.execute()
