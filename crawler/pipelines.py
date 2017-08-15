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
        self.operations = {}  # for bulk write
        self.OP_LIMIT_SIZE = 100

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
	op = UpdateOne({ key: item[key] }, { '$set': dict(item) }, upsert=True)
	self.push_operation(op, clt)

    """
    method: append info into existed item
    input @item: scrapy item
    input @clt: pymongo collection
    input @key: primary key
    """
    def append(self, item, clt, key):
        key_index = item.keys().index(key)
        arr_key = item.keys()[1-key_index]  # get another key
        op = UpdateOne({ key: item[key] }, { '$addToSet': { arr_key: item[arr_key] }} )
	self.push_operation(op, clt)

    def push_operation(self, op, clt):
	ops = self.operations
	if clt.name not in ops:
	    ops[clt.name] = []
	reqs = ops[clt.name]
        reqs.append(op)
	if len(reqs) >= self.OP_LIMIT_SIZE:
	    self.bulk_write(clt, reqs)
	    self.operations[clt.name] = []
	    log.info('size={}'.format(len(self.operations[clt.name])))

    """
    method: write multiple requests into db
    input @clt: collection
    input @reqs: requests
    """
    def bulk_write(self, clt, reqs):
        try:
   	    result = clt.bulk_write(reqs)
	    log.info('add {NUM} into collection {CLT_NAME} successfully, now having {COUNT} documents'.format(NUM=len(reqs), CLT_NAME=clt.name, COUNT=clt.count()))
        except Exception as e:
	    log.error('occur errors when adding into collection {CLT_NAME}, error info: {ERROR}'.format(CLT_NAME=clt.name, ERROR=e))


