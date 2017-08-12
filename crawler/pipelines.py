# -*- coding: utf-8 -*-

'''
    File name: pipelines.py
    Author: hackrflov
    Date created: 8/11/2017
    Python version: 2.7
'''

import logging
log = logging.getLogger('scrapy.pipeline')

from pymongo import MongoClient
from crawler.items import UserItem, VideoItem, DanmakuItem


class DstPipeline(object):
    def process_item(self, item, spider):
        return item

class BilibiliPipeline(object):
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
        clt = db[clt_name]
        if len(item) > 2:
            self.upsert(item, clt, key)
        elif len(item) == 2:
            self.append(item, clt, key)

    """
    method: insert & update item
    input @item: scrapy item
    input @clt: pymongo collection
    input @key: primary key
    """
    def upsert(self, item, clt, key):
        try:
            clt.update({ key: item[key] }, { '$set': dict(item) }, upsert=True)
            log.info('add {key} into collection {CLT_NAME} successfully, now having {COUNT} documents'.format(key=item[key], CLT_NAME=clt.name, COUNT=clt.count()))
        except Exception as e:
            log.error('occur errors when adding into collection {CLT_NAME}, item = {ITEM}, error info: {ERROR}'.format(CLT_NAME=clt.name, ITEM=item, ERROR=e))

    def append(self, item, clt, key):
        key_index = item.keys().index(key)
        arr_key = item.keys()[1-key_index]  # get another key
        clt.update({ key: item[key] }, { '$addToSet': { arr_key: item[arr_key] }} )
        log.info('successfully add {arr_key} into item {pk}, values: {v}'.format(arr_key=arr_key,pk=item[key],v=item[arr_key]))

