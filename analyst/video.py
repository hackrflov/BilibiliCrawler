#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: video.py
    Date: 08/18/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

from pymongo import MongoClient
from pprint import pprint

client = MongoClient()
db = client.bilibili

"""
method: list videos which contain certain tag, i.e. BGM, 镇站之宝, 万恶之源
"""
def hot_tag():
    tag = '万恶之源'
    docs = db.video.find( { 'tags' : { '$in' : [tag] } } )#.sort({ 'favorates' : -1 })
    show(docs)


"""
method: print every doc inside
"""
def show(docs):
    for doc in docs:
        pprint(doc)

if __name__ == '__main__':
    hot_tag()

