# -*- encoding: utf-8 -*-
import scrapy
import re
import json
from bs4 import BeautifulSoup
import pymongo
from dst.items import BilibiliItem

class BilibiliSpider(scrapy.Spider):
    name = 'bilibili'

    def clearDb(self):
        client = pymongo.MongoClient()
        db = client.bilibili
        db.user.delete_many({})
        db.video.delete_many({})
        db.danmaku.delete_many({})

    def start_requests(self):
        self.clearDb()
        self.limit = 1
        # user info
        for mid in range(self.limit):
            url = 'https://space.bilibili.com/ajax/member/GetInfo?mid={MID}'.format(MID=mid)
            headers = {'Referer': 'https://www.bilibili.com'}
            yield scrapy.Request(url=url, method='POST', headers=headers, callback=self.parse)
        # video info
        for aid in range(self.limit):
            url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid={AID}'.format(AID=aid)
            #yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print 'now parse url: %s' %response.url
        print response.body
        print response.meta
        print response.request.headers

    '''
    用于解析弹幕文件
    '''
    def parseDanmaku(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        for node in soup.find_all('d'):
            text = node.string
            item = BilibiliItem(text=text)
            yield item

    '''
    用于解析推荐视频文件
    '''
    def parseRecommend(self, response):
        data = json.loads(response.body)['data']
        for v_msg in data:
            aid = v_msg['aid']
            next_url = 'https://www.bilibili.com/video/av%s/' %aid
            yield scrapy.Request(url=next_url, callback=self.parse)

    def closed(self, reason):
        client = pymongo.MongoClient()
        db = client.bilibili
        dmk = db.danmaku
        for doc in dmk.find(limit=20).sort('count', pymongo.DESCENDING):
            print doc

