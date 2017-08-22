import os
import sys

if len(sys.argv) >= 2:  # with extra argument
    if len(sys.argv) >= 3:
        os.system('scrapy crawl bilibili -a collection={c} -a start_num={n}'.format(c=sys.argv[1],n=sys.argv[2]))
    else:
        os.system('scrapy crawl bilibili -a collection={}'.format(sys.argv[1]))
else:
    os.system('scrapy crawl bilibili')

