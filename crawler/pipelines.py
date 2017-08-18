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
        clt = self.db[item._db_name]
        key = item._unique_key

        # check index
        clt.create_index(key)

        # push into db in two ways
        if item._type == 'default':
            self.upsert(item, clt, key)
        elif item._type == 'append':
            self.append(item, clt, key)

    """
    method: insert & update item
    input @clt: pymongo collection
    """
    def upsert(self, item, clt, key):
        op = UpdateOne({ key: item[key] }, { '$set': item.valid_fields() }, upsert=True)
        self.push_operation(op, clt)

    """
    method: append details into existed item
    input @clt: pymongo collection
    """
    def append(self, item, clt, key):
        fields = item.valid_fields()
        for add_key in fields.keys():
            if add_key != key:  # not equal to unique key
                op = UpdateOne({ key: item[key] }, { '$addToSet': { add_key: { '$each' : item[add_key] } } } )
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


