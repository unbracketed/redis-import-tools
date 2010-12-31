# redis-import-set
import sys
from csv import reader
from itertools import count, groupby, islice

import redis


if __name__ == '__main__':
	
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    try:
        keyname = sys.argv[1]
    except IndexError:
        raise Exception("You must specify the name for the Set")

    for k, _ in groupby(reader(sys.stdin, delimiter='\t'), 
            lambda x:x[0]):
        pipeline_redis.sadd(keyname, k)
        count += 1
        if not count % 10000:
        	pipeline_redis.execute()


