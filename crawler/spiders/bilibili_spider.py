#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: bilibili_spider.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import sys
import re
import json
import pdb

import scrapy
from scrapy import selector, signals
import requests
import pymongo
from crawler.items import UserItem, VideoItem, DanmakuItem, BangumiItem
from tenacity import retry
import logging
log = logging.getLogger('scrapy.spider')


class BilibiliSpider(scrapy.Spider):

    name = 'bilibili'

    def __init__(self, collection='', *args, **kwargs):
        super(BilibiliSpider, self).__init__(*args, **kwargs)
        self.collection = collection

    """
    method: delete all existing data
    """
    def clear_db(self):
        client = pymongo.MongoClient()
        db = client.bilibili
        #db.user.delete_many({})
        #db.video.delete_many({})
        #db.danmaku.delete_many({})

    def start_requests(self):
        # Uncomment to crawl totally fresh
        # self.clear_db()

        # use cmd input to fetch specific data
        clt = self.collection
        FETCH_LIMIT = 10000000

        # Fetch for user
        if clt in ['user','']:
            for i in range(FETCH_LIMIT):
                mid = 1 + i
                #mid = 871257 + i  # last record
                #url = 'http://api.bilibili.com/cardrich?mid={}'.format(mid)
                url = 'https://app.bilibili.com/x/v2/space?vmid={}&build=1&ps=1'.format(mid)
                request = scrapy.Request(url=url, callback=self.parse_user_seed)
                #request.meta['force_proxy'] = True
                request.meta['mid'] = mid
                yield request

        # Fetch for video
        if clt in ['video','']:
            for i in range(FETCH_LIMIT):
                #aid = 1 + i
                aid = 937686 + i  # last record
                #url = 'http://www.bilibili.com/widget/getPageList?aid={}'.format(aid)
                url = 'http://m.bilibili.com/video/av{}.html'.format(aid)
                request = scrapy.Request(url=url, callback=self.parse_video_seed)
                request.meta['aid'] = aid
                yield request

        # Fetch for danmaku
        if clt in ['danmaku','']:
            for i in range(FETCH_LIMIT):
                cid = 1 + i
                danmaku_url = 'http://comment.bilibili.com/rolldate,{}'.format(cid)
                request = scrapy.Request(url=danmaku_url, callback=self.parse_danmaku_seed)
                request.meta['cid'] = cid
                yield request

        # Fetch for bangumi
        if clt in ['bangumi','']:
            for i in range(FETCH_LIMIT):
                sid = 1 + i
                url = 'http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver?'.format(sid)
                request = scrapy.Request(url=url, callback=self.parse_bangumi)
                request.meta['sid'] = sid
                yield request


    def parse_user_seed(self, response):
        data = json.loads(response.body)['data']

        # user card
        data = data['card']
        data['mid'] = int(data['mid'])  # change to int
        data['level'] = data['level_info']['current_level']
        data['nameplate'] = data['nameplate']['name']

        # live & fav & tag & seanson & game
        if 'favourate' in data:
            f = data['favourate']
            data['fav'] = f['count']
            data['favs'] = [item['fid'] for item in f['item']]
        if 'tags' in data:
            data['tags'] = [tag['tag_name'] for tag in data['tags']]

        data['roomid']  = data['live'].get('roomid')  if 'live'   in data else ''
        data['game']    = data['game'].get('count')   if 'game'   in data else ''
        data['seanson'] = data['season'].get('count') if 'season' in data else ''

        user = UserItem()
        user.fill(data)
        yield user

        """
        # next request - detail
        mid = response.meta['mid']
        url = 'https://space.bilibili.com/ajax/member/GetInfo'
        request = scrapy.FormRequest(url=url, formdata={'mid':str(mid)}, callback=self.parse_user_detail)
        request.meta['mid'] = mid
        yield request

        # next request - favorates
        mid = response.meta['mid']
        url = 'https://api.bilibili.com/x/v2/fav/folder?vmid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_fav_seed)
        request.meta['mid'] = mid
        yield request

        # next request - Bangumi
        url = 'https://space.bilibili.com/ajax/Bangumi/getList?mid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_subscribe)
        request.meta['mid'] = mid
        yield request
        """


    def parse_video_seed(self, response):

        # parse html
        raw = re.search('(?<=STATE__ = ).*?(?=;\n</script>)', response.body).group()
        wrap = json.loads(raw)
        data = wrap['videoReducer']

        # extract tag list
        if 'videoTag' in wrap:
            tag_wrap = wrap['videoTag'].replace('\\"','"')  # delete all blackslash
            tags = json.loads(tag_wrap)['data']
            for i, tag in enumerate(tags):
                tags[i] = tag['tag_name']
            data['tags'] = tags

        # yield item
        video = VideoItem()
        video.fill(data)
        yield video

        # next request: video stat
        stat_url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={}'.format(aid)
        yield scrapy.Request(url=stat_url, callback=self.parse_video_stat)


    def parse_video_stat(self, response):
        data = json.loads(response.body)['data']
        video = VideoItem()
        video.fill(data)
        yield video

    def parse_user_detail(self, response):
        data = json.loads(response.body)['data']
        user = UserItem()
        user.fill({'mid':response.meta['mid'], 'playNum':data['playNum']})
        yield user


    def parse_user_fav_seed(self, response):
        data = json.loads(response.body)['data']
        mid = response.meta['mid']
        favs = []
        for folder in data:
            fid = folder['fid']
            count = folder['cur_count']
            ps = 30
            pages = count / ps + 1
            for pn in range(1,pages+1):
                url = 'https://api.bilibili.com/x/v2/fav/video?vmid={mid}&fid={fid}&pn={pn}&ps={ps}'.format(mid=mid,fid=fid,pn=pn,ps=ps)
                request = scrapy.Request(url=url, callback=self.parse_user_fav)
                request.meta['mid'] = mid
                yield request

    def parse_user_fav(self, response):
        data = json.loads(response.body)['data']['archives']
        mid = response.meta['mid']
        favs = [f['aid'] for f in data]
        user = UserItem()
        user.fill({'mid':response.meta['mid'], 'favs': favs })
        user._type = 'append'
        yield user


    def parse_user_subscribe(self, response):
        raw = json.loads(response.body)
        data = raw['data']
        mid = response.meta['mid']
        max_page = data['pages']
        if max_page == 0:
            return

        subs = [f['season_id'] for f in data['result']]
        user = UserItem()
        user.fill({'mid': mid, 'subscribe': subs })
        user._type = 'append'
        yield user

        # next page
        if 'pn' in response.meta:
            pn = response.meta['pn']
            if pn >= max_page:
                return
        else:
            pn = 1

        pn = pn + 1
        url = 'https://space.bilibili.com/ajax/Bangumi/getList?mid={mid}&pages={pn}'.format(mid=mid,pn=pn)
        request = scrapy.Request(url=url, callback=self.parse_user_subscribe)  # call itself repeatly
        request.meta['mid'] = mid
        request.meta['pn'] = pn
        yield request

    def parse_danmaku_seed(self, response):
        cid = response.meta['cid']
        data = response.body
        if data == '':
            url = 'http://comment.bilibili.com/{}.xml'.format(cid)
            request = scrapy.Request(url=url, callback=self.parse_danmaku)
            request.meta['cid'] = cid
            yield request
        else:
            rolldates = json.loads(data)
            for rolldate in rolldates:
                ts = rolldate['timestamp']
                url = 'http://comment.bilibili.com/dmroll,{TS},{CID}'.format(TS=ts,CID=cid)
                request = scrapy.Request(url=url, callback=self.parse_danmaku)
                request.meta['cid'] = cid
                yield request

    def parse_danmaku(self, response):
        data = response.xpath('//d')
        for row in data:
            ps = row.xpath('@p').extract()[0]  # param string
            pl = ps.split(',')  # param list
            dmk = DanmakuItem()
            dmk['playTime'] = int(pl[0])
            dmk['mode'] = int(pl[1])
            dmk['fontsize'] = int(pl[2])
            dmk['color'] = int(intpl[3])
            dmk['timestamp'] = int(pl[4])
            dmk['pool'] = int(pl[5])
            dmk['hashID'] = pl[6]
            dmk['uid'] = int(pl[7])
            dmk['cid'] = response.meta['cid']
            try: # This may not contain any text
                dmk['msg'] = row.xpath('text()').extract()[0]
            except:
                pass
            yield dmk


    def parse_bangumi(self, response):
        sid = response.meta['sid']
        raw = re.search('(?<=seasonListCallback\().*?(?=\);)', response.body).group()
        data = json.loads(raw)['result']
        data['sid'] = sid
        tags = []
        for t in data['tags']:
            tags.append(t['tag_name'])
        data['tags'] = tags

        # yield item
        bangumi = BangumiItem()
        bangumi.fill(data)
        yield bangumi
