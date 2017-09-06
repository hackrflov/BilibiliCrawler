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

