#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: bili_util.py
    Date: 08/21/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""


from pymongo import MongoClient
from datetime import datetime
import random

client = MongoClient()
db = client.bilibili

class BiliUtil():

    clt_name = ''

    def list(self):
        print "type '$ python user.py [func name]' with func names from following list:"
        for name in dir(self):
            if name not in dir(BiliUtil): # don't list func in BiliUtil
                print '-', name
        print '+', 'find_by_rand'

    def find_by_field(self, key=''):
        if key == '':
            docs = db[self.clt_name].find().limit(10)
        else:
            docs = db[self.clt_name].find({}, {key:1}).limit(10)
        self.show(docs)

    def find_by_rand(self):
        docs = db[self.clt_name].aggregate([ { '$sample' : { 'size' : 10 } } ])
        self.show(docs)

    def sort_by_key(self, key):
        docs = db[self.clt_name].find().sort(key,-1).limit(10)
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
        for doc in docs:
            print '{'
            sorted_items = sorted(doc.items(), key=lambda t: t[0])
            for (key, value) in sorted_items:
                print '    ', key, ':',
                if type(value) == list:
                    print '[',
                    for v in value:
                        print v, ',',
                    print '],'
                elif type(value) == int:
                    dt = datetime.fromtimestamp(value)
                    if dt.year >= 2000:
                        print dt.strftime('%Y-%m-%d %H:%M'), ','
                    else:
                        print value, ','
                else:
                    print value, ','
            print '}'
