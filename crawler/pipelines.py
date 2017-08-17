#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: pipelines.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import logging
log = logging.getLogger('scrapy.pipeline')

from pymongo import MongoClient, UpdateOne
from crawler.items import UserItem, VideoItem, DanmakuItem, BangumiItem


class DstPipeline(object):
    def process_item(self, item, spider):
        return item

class BilibiliPipeline(object):

    # settings
    OP_LIMIT_SIZE = 100

    def __init__(self):
        self.operations = {}  # for bulk write
        client = MongoClient()
        self.db = client.bilibili

    def process_item(self, item, spider):

        # get collection and unique key
        clt = self.db[item.db_name()]
        key = item.unique_key()

        # check index
        clt.create_index(key)

        # push into db in two ways
        if len(item) > 2:
            self.upsert(item, clt, key)
        elif len(item) == 2:
            self.append(item, clt, key)

    """
    method: insert & update item
    input @clt: pymongo collection
    """
    def upsert(self, item, clt, key):
        op = UpdateOne({ key: item[key] }, { '$set': dict(item) }, upsert=True)
        self.push_operation(op, clt)

    """
    method: append details into existed item
    input @clt: pymongo collection
    """
    def append(self, item, clt, key):
        key_index = item.keys().index(key)
        arr_key = item.keys()[1-key_index]  # get another key
        op = UpdateOne({ key: item[key] }, { '$addToSet': { arr_key: item[arr_key] }} )
        self.push_operation(op, clt)

    """
    method: collect multiple operations
    input @op: one operation applied on item
    """
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


