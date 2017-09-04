#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: bilibili_spider.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import re
import json
import logging
log = logging.getLogger('scrapy.spider')

import scrapy
import requests
from crawler.items import UserItem, VideoItem, DanmakuItem, BangumiItem
from datetime import datetime

class BilibiliSpider(scrapy.Spider):

    name = 'bilibili'

    def __init__(self, target='', start=1, end=10000000, *args, **kwargs):
        super(BilibiliSpider, self).__init__(*args, **kwargs)
        self.clt = target
        self.sn = int(start)
        self.en = int(end)

    def start_requests(self):

        # Fetch for user
        if self.clt in ['user','']:
            for mid in range(self.sn, self.en):
                url = 'https://app.bilibili.com/x/v2/space?vmid={}&build=1&ps=1'.format(mid)
                request = scrapy.Request(url=url, callback=self.parse_user_seed)
                yield request

        # Fetch for video
        if self.clt in ['video','']:
            for aid in range(self.sn, self.en):
                #url = 'http://www.bilibili.com/widget/getPageList?aid={}'.format(aid)
                url = 'http://m.bilibili.com/video/av{}.html'.format(aid)
                request = scrapy.Request(url=url, callback=self.parse_video_seed)
                request.meta['aid'] = aid
                yield request

        # Fetch for danmaku
        if self.clt in ['danmaku','']:
            for cid in range(self.sn, self.en):
                #danmaku_url = 'http://comment.bilibili.com/rolldate,{}'.format(cid)
                url = 'http://comment.bilibili.com/{}.xml'.format(cid)
                request = scrapy.Request(url=url, callback=self.parse_danmaku)
                request.meta['cid'] = cid
                yield request

        # Fetch for bangumi
        if self.clt in ['bangumi','']:
            for sid in range(self.sn, self.en):
                url = 'http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver?'.format(sid)
                request = scrapy.Request(url=url, callback=self.parse_bangumi)
                request.meta['sid'] = sid
                yield request

    #==================== USER PART ====================#

    def parse_user_seed(self, response):
        raw = json.loads(response.body)['data']

        # user card
        data = raw['card']
        mid = int(data['mid'])
        data['mid'] = mid
        data['vip'] = data['vip']['vipType']
        data['level'] = data['level_info']['current_level']
        data['nameplate'] = data['nameplate']['name']
        data['regtime'] = datetime.fromtimestamp(data['regtime'])

        # elec & live & article
        data['elec'] = raw['elec'].get('total') if 'elec' in raw else ''
        data['live'] = raw['live'].get('roomid') if 'live' in raw else ''
        data['article'] = raw['archive'].get('count') if 'archive' in raw else ''
        data['setting'] = raw['setting']

        # atttentions
        if data['attention'] > 0:
            url = 'http://api.bilibili.com/cardrich?mid={}'.format(mid)
            request = scrapy.Request(url=url, callback=self.parse_user_attentions)
            request.meta['mid'] = mid
            yield request

        # favourite
        tab = raw.get('favourite')
        if tab:
            data['folder'] = [ { 'id':t['fid'], 'name':t['name'] } for t in tab['item'] ]
            for fid in data['folder']:
                url = 'https://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}'.format(m=mid, f=fid)
                request = scrapy.Request(url=url, callback=self.parse_user_favorite)
                request.meta['mid'] = mid
                request.meta['fid'] = fid
                request.meta['pn'] = 1
                yield request
        elif raw['setting']['fav_video'] == 0:
            url = 'https://api.bilibili.com/x/v2/fav/folder?vmid={}'.format(mid)
            request = scrapy.Request(url=url, callback=self.parse_user_folder)
            request.meta['mid'] = mid
            yield request

        # community
        tab = raw.get('community')
        if tab:
            if tab['count'] <= 20:
                data['community'] = [t['id'] for t in tab['item']]
            else:
                url = 'https://app.bilibili.com/x/v2/space/community?vmid={}'.format(mid)
                request = scrapy.Request(url=url, callback=self.parse_user_community)
                request.meta['mid'] = mid
                request.meta['pn'] = 1
                yield request

        # bangumi
        tab = raw.get('season')
        if tab:
            if tab['count'] <= 20:
                data['bangumi'] = [ int(t['param']) for t in tab['item']]
            else:
                url = 'https://app.bilibili.com/x/v2/space/bangumi?vmid={}'.format(mid)
                request = scrapy.Request(url=url, callback=self.parse_user_bangumi)
                request.meta['mid'] = mid
                request.meta['pn'] = 1
                yield request

        # tag
        if 'tag' in raw:
            url = 'https://space.bilibili.com/ajax/tags/getSubList?mid={}'.format(mid)
            request = scrapy.Request(url=url, callback=self.parse_user_tag)
            request.meta['mid'] = mid
            yield request

        # game
        tab = raw.get('game')
        if tab:
            data['game'] = [t['id'] for t in tab['item']]

        # yield item
        user = UserItem()
        user.fill(data)
        yield user

    def parse_user_attentions(self, response):
        data = json.loads(response.body)['data']['card']
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'attentions': data['attentions'] })
        yield user

    def parse_user_folder(self, response):
        data = json.loads(response.body)['data']
        flds  = [ { 'id':t['fid'], 'name':t['name'] } for t in data]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'folder': flds })
        yield user

        # crawl videos inside each folder
        for fid in flds:
            url = 'https://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}'.format(m=mid, f=fid)
            request = scrapy.Request(url=url, callback=self.parse_user_favorite)
            request.meta['mid'] = mid
            request.meta['fid'] = fid
            request.meta['pn'] = 1
            yield request

    def parse_user_favorite(self, response):
        data = json.loads(response.body)['data']
        favs = [ { 'id':t['aid'], 'dt':datetime.fromtimestamp(t['fav_at']) } for t in data['archives'] ]  # aid & datetime pair
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'favorite': favs }, item_type='append' )
        yield user

        # crawl next page
        fid = response.meta['fid']
        pn = response.meta['pn']
        ps = 30
        total = data['total']
        if pn * ps < total:
            next_pn = pn + 1
            url = 'https://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}&pn={p}'.format(m=mid, f=fid, p=next_pn)
            request = scrapy.Request(url=url, callback=self.parse_user_favorite)
            request.meta['mid'] = mid
            request.meta['fid'] = fid
            request.meta['pn'] = next_pn
            yield request

    def parse_user_community(self, response):
        data = json.loads(response.body)['data']
        cmu = [t['id'] for t in data['item']]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'community': cmu }, item_type='append' )
        yield user

        # crawl next page
        pn = response.meta['pn']
        ps = 20
        total = data['count']
        if pn * ps < total:
            next_pn = pn + 1
            url = 'https://app.bilibili.com/x/v2/space/community?vmid={m}&pn={p}'.format(m=mid, p=next_pn)
            request = scrapy.Request(url=url, callback=self.parse_user_community)
            request.meta['mid'] = mid
            request.meta['pn'] = next_pn
            yield request

    def parse_user_bangumi(self, response):
        data = json.loads(response.body)['data']
        bgm = [int(t['param']) for t in data['item']]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'bangumi': bgm }, item_type='append' )
        yield user

        # crawl next page
        pn = response.meta['pn']
        ps = 20
        total = data['count']
        if pn * ps < total:
            next_pn = pn + 1
            url = 'https://app.bilibili.com/x/v2/space/bangumi?vmid={m}&pn={p}'.format(m=mid, p=next_pn)
            request = scrapy.Request(url=url, callback=self.parse_user_bangumi)
            request.meta['mid'] = mid
            request.meta['pn'] = next_pn
            yield request

    def parse_user_tag(self, response):
        data = json.loads(response.body)['data']
        tag = [t['name'] for t in data['tags']]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'tag': tag })
        yield user


    #==================== VIDEO PART ====================#

    def parse_video_seed(self, response):

        # parse html
        raw = re.search('(?<=STATE__ = ).*?(?=;\n</script>)', response.body).group()
        wrap = json.loads(raw)
        data = wrap['videoReducer']
        data['pubdate'] = datetime.fromtimestamp(data['pubdate'])
        aid = data['aid']

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
        request = scrapy.Request(url=stat_url, callback=self.parse_video_stat)
        request.meta['aid'] = aid
        yield request


    def parse_video_stat(self, response):
        data = json.loads(response.body)['data']
        data['aid'] = response.meta['aid']
        video = VideoItem()
        video.fill(data)
        yield video

    #==================== DANMAKU PART ====================#

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

    #==================== BANGUMI PART ====================#

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
