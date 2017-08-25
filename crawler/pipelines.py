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
from crawler.items import *

class BilibiliPipeline(object):

    # settings
    OP_LIMIT_SIZE = 100

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def __init__(self, settings):
        self.operations = {}  # for bulk write
        host = settings.get('MONGO_HOST')
        db = settings.get('MONGO_DB')
        usr = settings.get('MONGO_USERNAME')
        pwd = settings.get('MONGO_PASSWORD')
        if usr and pwd:
            uri = 'mongodb://{u}:{p}@{h}/{d}'.format(u=usr,p=pwd,h=host,d=db)
        else:
            uri = 'mongodb://{h}/{d}'.format(h=host,d=db)
        client = MongoClient(uri)
        self.db = client[db]


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
        op = UpdateOne({ key: item[key] }, { '$set': dict(item) }, upsert=True)
        self.push_operation(op, clt)

    """
    method: append details into existed item
    input @clt: pymongo collection
    """
    def append(self, item, clt, key):
        for (add_key, add_value) in item.items():
            if add_key != key:  # not equal to unique key
                op = UpdateOne({ key: item[key] }, { '$addToSet': { add_key: { '$each' : add_value } } } )
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


