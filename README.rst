redis-import-tools
==================

A collection of utilities for importing data into Redis

Commands
--------

redis-import-set
    Create a Redis Set from a column of values in a text file


Installation
------------

It is assumed that you have Redis version >= 1.3 installed and configured.

::

    pip install redis-import-tools


Introduction
------------

Let's start with a trivial example. We'd like to load our local words dictionary into a Redis set. One approach might be::

    $ cat /usr/share/dict/words \
    | xargs -d "\n" -I word redis-cli sadd engdict word  > /dev/null

We're piping the contents of the dictionary file to `xargs`, which will run an ``SADD`` command for each
word in the dictionary and add it to a set called ``engdict``.

While the one-liner is nice, performance was terrible::

    real    5m36.977s
    user    0m3.560s
    sys     1m17.490s

We can observe that we're making one query to Redis for each word in the dictionary and there are::

    
    $ wc -l /usr/share/dict/words
    98569 /usr/share/dict/words

98569 words in the dictionary. Five minutes to get 100,000 requests into Redis isn't acceptable. Also, it looks like some words didn't make 
it into the set::

    $ redis-cli
    redis> scard engdict
    (integer) 95426


      
One obvious place for improvement is to use the Redis pipelining feature to cut down significantly on the number of requests made.
I see redis-cli as a convenience tool and I suspect it wasn't designed with the use case of frequently forking new processes. By building on
the solid redis-py Redis client library we can come up with some basic utilities that will offer great performance with some flexibility 
for populating Redis from data sources such as CSV/TSV files. 

With code like the following, we can send data to Redis in batches (10000 values per request)::

    r = redis.Redis()
    pipeline_redis = r.pipeline()
    count = 0
    for line in sys.stdin:
        pipeline_redis.sadd(keyname, line.rstrip())
        count += 1
        if not count % 10000:
            pipeline_redis.execute()
    pipeline_redis.execute()

This code is the basic idea for the redis-import-set command. Here's how to use the command to perform the desired operation::

    $ redis-import-set engdict < /usr/share/dict/words

Performance is now very acceptable::

    real    0m2.838s
    user    0m2.530s
    sys     0m0.050s

And the set count matches the input count::

    redis> scard engdict
    (integer) 98569


About Filtering, Sorting, and Compression...
--------------------------------------------

Often you will be starting with an input set that contains extraneous data (columns and/or rows you won't need). 

The performance characteristics of these data processing steps can vary depending on where they are handled. For example, 
the Python ZipFile streaming appeared to add significant overhead under scenarios I tested. I may add some basic fallbacks
for decompressing the input source in the future and I'm also deciding what features in general I might want to support for I/O with
compressed/archive data formats. Since decompressing data is always
a first operation it easiest just to rely on the native OS compression tools and allow the redis-import-tools commands to 
assume (uncompressed) textual input.

Python CSV seems to add a minimal amount of overhead so leaving it in is worthwhile since it probably more robust than
naively using ``string.split()``


Case Study
----------


Using the corpus of English 1-grams from Google Books: TODO

The first archive contains 29232733 rows of which 420044 are unique. 

Extract the first column into a file which we'll later use as input redis-import-set::

    $ time unzip -p googlebooks-eng-us-all-1gram-20090715-0.csv.zip | cut -f 1 | uniq > eng-us-all-1gram-0-uniq-grams

    real    0m12.706s
    user    0m15.820s
    sys     0m1.460s


Import as a set::

    $ time redis-import-set 1g < eng-us-all-1gram-0-uniq-grams

    real    0m12.995s
    user    0m11.130s
    sys     0m0.120s

Let's see how it fares if the input has duplicates::

    $ googlebooks-eng-us-all-1gram-20090715-0.csv.zip | cut -f 0 > eng-us-all-1gram-0-grams
    $ time redis-import-set 1g < eng-us-all-1gram-0-grams

    real    0m31.068s
    user    0m28.910s
    sys     0m0.160s

Internally redis-import-set is using ``itertools.groupby`` to avoid sending redundant ``SADD`` operations for repeated
entries. 

Here is for just using the raw CSV file, taking advantage of the `redis-import-set` behavior to default to the 
first column::

    real    0m39.420s
    user    0m37.200s
    sys     0m0.360s

This is good considering that the input size of the input with duplicates is 70x bigger yet the execution time only tripled
from the unique inputs case.

What happens if we try to process unsorted data with many duplicates? The groupby filter won't have any effect
and consequently we'll be sending many more requests than needed, containing mostly redundant data. To illustrate
we'll cut the years column out of the corpus file giving us a huge input count containing only a few hundred 
distinct values::

    # Slice out the years column from the corpus
    $ time unzip -p googlebooks-eng-us-all-1gram-20090715-0.csv.zip | cut -f 2 > eng-us-all-1gram-0-years

    real    0m14.114s
    user    0m13.190s
    sys     0m1.320s

    $ wc -l eng-us-all-1gram-0-years
    29232733

    $ time redis-import-set years < eng-us-all-1gram-0-years

    real    13m50.783s
    user    12m39.700s
    sys     0m4.450s

Ouch! This is problematic. However, we can still workaround this by using a Python Set internally to track which
items we've already sent to ``SADD``. After making this change, we have::

    time redis-import-set years < eng-us-all-1gram-0-years

    real    0m26.108s
    user    0m25.970s
    sys     0m0.060s

Back in business. For many inputs the distinct count may be a small percentage of the total inputs but otherwise
it won't be desirable to be automatically cache set members in the command. A forthcoming change will require
use of a command line argument to signify that the input is unsorted and to utilize the cache. 
