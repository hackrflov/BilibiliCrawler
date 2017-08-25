import os
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start your powerful crawler :)')
    parser.add_argument('-r','--range', nargs=2, metavar=('start','end'), type=int, help='specify crawl range, e.g. 10000 20000')
    parser.add_argument('target', nargs='?', default='', help='crawl specific target, e.g. user')
    args = parser.parse_args()
    cmd = 'scrapy crawl bilibili -a target={t} -a start={s} -a end={e}'.format(t=args.target, s=args.range[0], e=args.range[1])
    os.system(cmd)
