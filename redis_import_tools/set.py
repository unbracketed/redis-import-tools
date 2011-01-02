"redis-import-set"
import sys
from csv import reader
from itertools import groupby

import redis


def handle(**kwargs):
    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
#    try:
#        keyname = sys.argv[1]
#    except IndexError:
#        raise Exception("You must specify the name for the Set")
    
    seen = set()
    for member, _ in groupby(reader(sys.stdin, delimiter='\t'),
    	                    lambda x:x[0]):
        if member not in seen:
            pipeline_redis.sadd(kwargs['key'], member.rstrip())
            count += 1
            seen.add(member)
            if not count % 10000:
                pipeline_redis.execute()
    pipeline_redis.execute()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tools for importing data into Redis.')
    parser.add_argument('-u', '--unsorted', action="store_true")
    parser.add_argument('key', required=True)
    options = parser.parse_args()
    
    handle(**options)


