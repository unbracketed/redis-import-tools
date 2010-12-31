import os
import sys
import time
from csv import reader
from glob import glob
from itertools import count, groupby
from optparse import OptionParser
from zipfile import ZipFile



if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-d', '--datadir', 
            help="Directory containing data files",
            metavar="DIR")

    options, args = parser.parse_args()

    if not options.datadir:
        #create a temp dir
        pass
    else:
    	datadir = options.datadir

    
    #for onegram_archive in glob(os.path.join(datadir, '*.zip')):
    t0 = time.clock()
    onegram_archive = glob(os.path.join(datadir, '*.zip'))[0]
    #archive_lines = count()
    archive_lines = 0
    zf = ZipFile(onegram_archive)
    archive_name = zf.namelist()[0]
    print archive_name
    for gram, _ in groupby(reader(zf.open(archive_name), delimiter='\t'),
                           lambda x:x[0]):
        archive_lines += 1
        if archive_lines % 100000 == 0:
            print archive_lines    
            print time.clock() - t0
            t0 = time.clock()
    
