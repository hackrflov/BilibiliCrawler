import os
import sys

if len(sys.argv) >= 2:  # with extra argument
    os.system('scrapy crawl bilibili -a collection={}'.format(sys.argv[1]))
else:
    os.system('scrapy crawl bilibili')

