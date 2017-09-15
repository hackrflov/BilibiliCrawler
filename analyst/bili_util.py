#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: bili_util.py
    Date: 08/21/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import re
import types
import random

from datetime import datetime
from pymongo import MongoClient
import pdb
import pprint

client = MongoClient('mongodb://bili_crawler:bilibili@127.0.0.1/bilibili')
db = client.bilibili

class BiliUtil():

    clt_name = ''
    db = db

    def list(self):
        print "type '$ python user.py [func name]' with func names from following list:"
        for name in dir(self):
            if name not in dir(BiliUtil): # don't list func in BiliUtil
                print '-', name
        print '+', 'find_by_rand'

    def find_by_field(self, key='', value=''):
        if key == '':
            docs = db[self.clt_name].aggregate([
                { '$sample' : { 'size' : 10 } }
            ])
        elif value == '':
            docs = db[self.clt_name].aggregate([
                { '$project' : { key : 1 } },
                { '$sample' : { 'size' : 10 } }
            ])
        elif type(value) != list:
            docs = db[self.clt_name].aggregate([
                { '$match' : { key : value } },
                { '$sample' : { 'size' : 10 } }
            ])
        else:
            docs = db[self.clt_name].aggregate([
                { '$match' : { key : { '$in' : value } } },
                { '$sample' : { 'size' : 10 } },
            ])
        self.show(docs)

    def find_by_rand(self):
        self.find_by_field()

    def join_rand(self, clt, key):
        docs = db[self.clt_name].aggregate([ { '$sample' : { 'size' : 10 } } ])
        for doc in docs:
            join_doc = db[clt].find({ key : doc[key] })
            self.show(join_doc)

    def sort_by_key(self, key, limit=10):
        docs = db[self.clt_name].find().sort(key,-1).limit(limit)
        self.show(docs)

    def count_by_key(self, key):
        docs = db[self.clt_name].aggregate([
            { '$group': { '_id': '${}'.format(key),
                          'count': { '$sum' : 1 } } },
            { '$sort' : { 'count' : -1 } }
        ])
        self.show(docs)

    """
    method: print every doc inside
    """
    def show(self, docs):
        # Convert to list
        docs = [doc for doc in docs]
        for doc in docs:
            s = pprint.pformat(doc)
            s = re.sub("u'|'", '', s)
            print s.decode('unicode-escape')
