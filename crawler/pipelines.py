# -*- coding: utf-8 -*-

'''
    File name: pipelines.py
    Author: hackrflov
    Date created: 8/11/2017
    Python version: 2.7
'''

import logging
log = logging.getLogger('scrapy.pipeline')

from pymongo import MongoClient, UpdateOne
from crawler.items import UserItem, VideoItem, DanmakuItem, BangumiItem


class DstPipeline(object):
    def process_item(self, item, spider):
        return item

class BilibiliPipeline(object):

    def __init__(self):
        self.items = []  # for insert_many
        self.BUFF_LIMIT = 100

    def process_item(self, item, spider):
        client = MongoClient()
        db = client.bilibili
        item_type = type(item)
        # set collection name and primary key
        if item_type == UserItem:
            clt_name = 'user'
            key = 'mid'
        elif item_type == VideoItem:
            clt_name = 'video'
            key = 'aid'
        elif item_type == DanmakuItem:
            clt_name = 'danmaku'
            key = 'uid'
        elif item_type == BangumiItem:
            clt_name = 'bangumi'
            key = 'sid'
        clt = db[clt_name]
        if len(item) > 2:
            self.bulk_upsert(item, clt, key)
        elif len(item) == 2:
            self.append(item, clt, key)

    """
    method: save items to queue, then insert & update them in one connection
    input @item: scrapy item
    input @clt: pymongo collection
    input @key: primary key
    """
    def bulk_upsert(self, item, clt, key):
        self.items.append(item)
        if len(self.items) >= self.BUFF_LIMIT:
            requests = []
            for item in self.items:
                operation = UpdateOne({ key: item[key] }, { '$set': dict(item) }, upsert=True)
                requests.append(operation)
            try:
                result = clt.bulk_write(requests)
                log.info('add {NUM} into collection {CLT_NAME} successfully, now having {COUNT} documents'.format(NUM=len(self.items), CLT_NAME=clt.name, COUNT=clt.count()))
            except Exception as e:
                log.error('occur errors when adding into collection {CLT_NAME}, items = {ITEMS}, error info: {ERROR}'.format(CLT_NAME=clt.name, ITEMS=self.items, ERROR=e))
            # clear list
            self.items = []

    def append(self, item, clt, key):
        key_index = item.keys().index(key)
        arr_key = item.keys()[1-key_index]  # get another key
        clt.update({ key: item[key] }, { '$addToSet': { arr_key: item[arr_key] }} )
        log.info('successfully add {arr_key} into item {pk}, values: {v}'.format(arr_key=arr_key,pk=item[key],v=item[arr_key]))

