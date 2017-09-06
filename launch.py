import os
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start your powerful crawler :)')
    parser.add_argument('-r','--range', nargs=2, metavar=('start','end'), type=int, help='specify crawl range, e.g. 10000 20000')
    #parser.add_argument('-p','--patch', action='store_true', dest='patch', default=1, help='crawl missing data')
    parser.add_argument('-p','--patch', dest='patch', nargs='*', help='crawl missing data')
    parser.add_argument('target', nargs='?', default='', help='crawl specific target, e.g. user')
    args = parser.parse_args()
    print args
    spider = 'bilibili' if args.patch is None else 'patch'
    cmd = 'scrapy crawl {p} -a target={t} -a start={s} -a end={e}'.format(p=spider, t=args.target, s=args.range[0], e=args.range[1])
    print cmd
    os.system(cmd)
