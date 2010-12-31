# redis-import-set
import fileinput
import sys
from csv import reader
from itertools import count, islice

import redis


if __name__ == '__main__':
	
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    try:
        keyname = sys.argv[1]
    except IndexError:
        raise Exception("You must specify the name for the Set")

    for line in reader(sys.stdin, delimiter='\t'):
        pipeline_redis.sadd(keyname, line[0])
        count += 1
        if not count % 10000:
        	pipeline_redis.execute()


