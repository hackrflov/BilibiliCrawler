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
from pprint import pprint

client = MongoClient()
db = client.bilibili

class BiliUtil():

    clt_name = ''

    def list(self):
        list_str =  """\
type '$ python user.py [func name]' with func names from following list:
- find_by_field
- sort_by_key
- count_by_key
"""
        print list_str

    def find_by_field(self, key=''):
        if key == '':
            docs = db[self.clt_name].find().limit(10)
        else:
            docs = db[self.clt_name].find({}, {key:1}).limit(10)
        self.show(docs)

    def find(self):
        self.find_by_field()

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
            pprint(doc)
