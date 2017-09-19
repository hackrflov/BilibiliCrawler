#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: patch_spider.py
    Date: 09/05/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import re
import json

from pymongo import MongoClient
from crawler.items import *
import crawler.settings as st
from datetime import datetime
import scrapy

import logging
log = logging.getLogger('scrapy.patch')

class PatchSpider(scrapy.Spider):

    name = 'patch'

    def __init__(self, target='', start=1, end=10000000, *args, **kwargs):
        super(PatchSpider, self).__init__(*args, **kwargs)
        self.clt = target
        self.sn = int(start)
        self.en = int(end)
        self.connect(st)

    def connect(self, settings):
        host = settings.MONGO_HOST
        db = settings.MONGO_DB
        usr = settings.MONGO_USERNAME
        pwd = settings.MONGO_PASSWORD
        if usr and pwd:
            uri = 'mongodb://{u}:{p}@{h}/{d}'.format(u=usr,p=pwd,h=host,d=db)
        else:
            uri = 'mongodb://{h}/{d}'.format(h=host,d=db)
        client = MongoClient(uri)
        self.db = client[db]

    def check_video(self, aid):
        doc = self.db.video.find_one({ 'aid' : aid })
        if doc is None or 'totalpage' not in doc:
            log.debug('now fetch video: {}'.format(aid))
            return self.fetch_video_seed(aid)
        elif 'coin' not in doc:
            log.debug('now fetch video stat: {}'.format(aid))
            return self.fetch_video_stat(aid)

    def start_requests(self):

        # Fetch for video
        if self.clt in ['video','']:
            for aid in range(self.sn, self.en):
                reqs = self.check_video(aid)
                if reqs:
                    for req in reqs:
                        yield req

        # Fecth for user
        if self.clt in ['user','']:
            for mid in range(self.sn, self.en):
                url = 'https://app.bilibili.com/x/v2/space?vmid={}&build=1&ps=1'.format(mid)
                request = scrapy.Request(url=url, callback=self.check_user)
                request.meta['mid'] = mid
                yield request

    def check_user(self, response):
        mid = response.meta['mid']
        doc = self.db.user.find_one({ 'mid' : mid })
        reqs = []

        if doc is None or 'name' not in doc:
            log.debug('now fetch user total: {}'.format(mid))
            reqs = self.parse_user_seed(response)
            reqs.append(self.fetch_user_attentions(mid))
        else:
            raw = json.loads(response.body)['data']
            if 'regtime' not in doc or 'birthday' not in doc:
                log.debug('now fetch user attentions: {}'.format(mid))
                reqs.append(self.fetch_user_attentions(mid))

            BIAS = 5

            # favourite
            tab = raw.get('favourite')
            if tab:
                folder_size = [ t['cur_count'] for t in tab['item'] ]
                correct_num = sum(folder_size)
                if correct_num > 0:
                    real_fav_list = doc.get('favorite')
                    if real_fav_list == None or len(real_fav_list) < correct_num - BIAS:
                        log.debug('now fetch user fav: {}'.format(mid))
                        reqs.append(self.fetch_user_fav(mid))

            # community
            tab = raw.get('community')
            if tab:
                correct_num = tab['count']
                real_cmu_list = doc.get('community')
                if real_cmu_list == None or len(real_cmu_list) < correct_num - BIAS:
                    log.debug('now fetch user community: {}'.format(mid))
                    reqs.append(self.fetch_user_community(mid))

            # bangumi
            tab = raw.get('season')
            if tab:
                correct_num = tab['count']
                real_bgm_list = doc.get('bangumi')
                if real_bgm_list == None or len(real_bgm_list) < correct_num - BIAS:
                    log.debug('now fetch user bangumi: {}'.format(mid))
                    reqs.append(self.fetch_user_bangumi(mid))

            # tag
            tab = raw.get('tag')
            if tab and 'tag' not in doc:
                log.debug('now fetch user tag: {}'.format(mid))
                reqs.append(self.fetch_user_tag(mid))

            # coin
            tab = raw.get('coin_archive')
            if tab and 'coin' not in doc:
                log.debug('now fetch user coin: {}'.format(mid))
                reqs.append(self.fetch_user_coin(mid))

        # yield requests & items
        if reqs:
            for req in reqs:
                yield req

    def fetch_user_attentions(self, mid):
        url = 'http://api.bilibili.com/cardrich?mid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_attentions)
        request.meta['mid'] = mid
        request.meta['enable_proxy'] = True
        return request

    def fetch_user_fav(self, mid):
        url = 'http://space.bilibili.com/ajax/fav/getboxlist?mid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_folder)
        request.meta['mid'] = mid
        return request

    def fetch_user_community(self, mid):
        url = 'https://app.bilibili.com/x/v2/space/community?vmid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_community)
        request.meta['mid'] = mid
        request.meta['pn'] = 1
        return request

    def fetch_user_bangumi(self, mid):
        url = 'https://space.bilibili.com/ajax/Bangumi/getList?mid={}&page=1'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_bangumi)
        request.meta['mid'] = mid
        request.meta['page'] = 1
        return request

    def fetch_user_tag(self, mid):
        url = 'https://space.bilibili.com/ajax/tags/getSubList?mid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_tag)
        request.meta['mid'] = mid
        return request

    def fetch_user_coin(self, mid):
        url = 'https://space.bilibili.com/ajax/member/getCoinVideos?mid={}'.format(mid)
        request = scrapy.Request(url=url, callback=self.parse_user_coin)
        request.meta['mid'] = mid
        return request


    def parse_user_seed(self, response):
        raw = json.loads(response.body).get('data')
        if not raw:
            return

        # user card
        data = raw['card']
        mid = int(data['mid'])
        data['mid'] = mid
        data['vip'] = data['vip']['vipType']
        data['level'] = data['level_info']['current_level']
        data['nameplate'] = data['nameplate']['name']

        # elec & live & archive
        data['elec'] = raw['elec'].get('total') if 'elec' in raw else ''
        data['live'] = raw['live'].get('roomid') if 'live' in raw else ''
        data['archive'] = raw['archive'].get('count') if 'archive' in raw else ''
        data['setting'] = { k: v for k, v in raw['setting'].iteritems() if v == 0 }

        # favourite
        tab = raw.get('favourite')
        if tab:
            data['folder'] = [ { 'id':t['fid'], 'name':t['name'] } for t in tab['item'] ]
            for f in data['folder']:
                fid = f['id']
                url = 'http://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}'.format(m=mid, f=fid)
                request = scrapy.Request(url=url, callback=self.parse_user_favorite)
                request.meta['mid'] = mid
                request.meta['fid'] = fid
                request.meta['pn'] = 1
                request.meta['enable_proxy'] = True
                yield request
        elif raw['setting']['fav_video'] == 0:
            yield self.fetch_user_favorite(mid)

        # community
        tab = raw.get('community')
        if tab:
            if tab['count'] <= 20:
                data['community'] = [t['id'] for t in tab['item']]
            else:
                yield self.fetch_user_community(mid)

        # bangumi
        tab = raw.get('season')
        if tab:
            if tab['count'] <= 20:
                data['bangumi'] = [ int(t['param']) for t in tab['item']]
            else:
                yield self.fetch_user_bangumi(mid)

        # tag
        tab = raw.get('tag')
        if tab:
            yield self.fetch_user_tag(mid)

        # coin
        tab = raw.get('coin_archive')
        if tab:
            yield self.fetch_user_coin(mid)

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
        regtime = datetime.fromtimestamp(data['regtime'])
        mid = response.meta['mid']
        try:
            birthday = datetime.strptime(data['birthday'], '%Y-%m-%d')
        except:
            birthday = None
        user = UserItem({ 'mid': mid, 'attentions': data['attentions'], 'regtime' : regtime,
                          'birthday': birthday, 'place': data['place'] })
        yield user

    def parse_user_folder(self, response):
        data = json.loads(response.body)['data']['list']
        flds = []
        for fld in data:
            if fld['name'] == u'默认收藏夹' and fld['count'] == 0:
                continue
            else:
                flds.append({ 'id':fld['fav_box'], 'name':fld['name'] })
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'folder': flds })
        yield user

        # crawl videos inside each folder
        for f in flds:
            fid = f['id']
            url = 'http://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}'.format(m=mid, f=fid)
            request = scrapy.Request(url=url, callback=self.parse_user_favorite)
            request.meta['mid'] = mid
            request.meta['fid'] = fid
            request.meta['pn'] = 1
            request.meta['enable_proxy'] = True
            yield request

    def parse_user_favorite(self, response):
        data = json.loads(response.body)['data']
        favs = [ { 'id':t['aid'], 'dt':datetime.fromtimestamp(t['fav_at']) } for t in data['archives'] ]  # aid & datetime pair
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'favorite': favs }, item_type='append' )
        yield user

        # crawl all other page
        pn = response.meta['pn']
        if pn == 1:
            fid = response.meta['fid']
            ps = 30
            pages = data['total'] / ps + 1
            for next_pn in range(2, pages+1):
                url = 'http://api.bilibili.com/x/v2/fav/video?vmid={m}&fid={f}&pn={p}'.format(m=mid, f=fid, p=next_pn)
                request = scrapy.Request(url=url, callback=self.parse_user_favorite)
                request.meta['mid'] = mid
                request.meta['fid'] = fid
                request.meta['pn'] = next_pn
                request.meta['enable_proxy'] = True
                yield request

    def parse_user_community(self, response):
        data = json.loads(response.body)['data']
        if not data:
            return

        # extract info
        cmu = [t['id'] for t in data['item']]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'community': cmu }, item_type='append' )
        yield user

        # crawl all other page
        pn = response.meta['pn']
        if pn == 1:
            ps = 20
            pages = data['count'] / ps + 1
            for next_pn in range(2, pages+1):
                url = 'https://app.bilibili.com/x/v2/space/community?vmid={m}&pn={p}'.format(m=mid, p=next_pn)
                request = scrapy.Request(url=url, callback=self.parse_user_community)
                request.meta['mid'] = mid
                request.meta['pn'] = next_pn
                yield request

    def parse_user_bangumi(self, response):
        data = json.loads(response.body)['data']
        if not data:
            return

        # extract info
        bgm = [int(t['season_id']) for t in data['result']]
        mid = response.meta['mid']
        user = UserItem({ 'mid': mid, 'bangumi': bgm }, item_type='append' )
        yield user

        # crawl all other pages
        page = response.meta['page']
        if page == 1:
            for next_page in range(2, data['pages']+1):
                url = 'https://space.bilibili.com/ajax/Bangumi/getList?mid={m}&page={p}'.format(m=mid, p=next_page)
                request = scrapy.Request(url=url, callback=self.parse_user_bangumi)
                request.meta['mid'] = mid
                request.meta['page'] = next_page
                yield request

    def parse_user_coin(self, response):
        data = json.loads(response.body)['data']
        if 'list' in data:
            videos = [t['aid'] for t in data['list']]
            mid = response.meta['mid']
            user = UserItem({ 'mid': mid, 'coin': videos })
            yield user

    def parse_user_tag(self, response):
        data = json.loads(response.body)['data']
        if 'tags' in data:
            tag = [t['name'] for t in data['tags']]
            mid = response.meta['mid']
            user = UserItem({ 'mid': mid, 'tag': tag })
            yield user


    #==================== VIDEO PART ====================#

    def fetch_video_seed(self, aid):
        url = 'http://m.bilibili.com/video/av{}.html'.format(aid)
        request = scrapy.Request(url=url, callback=self.parse_video_seed)
        request.meta['aid'] = aid
        yield request

    def fetch_video_stat(self, aid):
        stat_url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={}'.format(aid)
        request = scrapy.Request(url=stat_url, callback=self.parse_video_stat)
        request.meta['aid'] = aid
        yield request

    def parse_video_seed(self, response):

        # parse html
        raw = re.search('(?<=STATE__ = ).*?(?=;\n</script>)', response.body).group()
        wrap = json.loads(raw)
        data = wrap['videoReducer']
        if 'aid' not in data:
            return
        data['pubdate'] = datetime.fromtimestamp(data['pubdate'])
        aid = data['aid']

        # extract tag list
        if 'videoTag' in wrap:
            tag_wrap = wrap['videoTag']
            tags = json.loads(tag_wrap)['data']
            if tags:
                for i, tag in enumerate(tags):
                    tags[i] = tag['tag_name']
                data['tags'] = tags

        # yield item
        video = VideoItem()
        video.fill(data)
        yield video

        # next request
        self.fetch_video_stat(aid)

    def parse_video_stat(self, response):
        data = json.loads(response.body)['data']
        data['aid'] = response.meta['aid']
        video = VideoItem()
        video.fill(data)
        yield video

