#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: user.py
    Date: 08/16/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

from pymongo import MongoClient
from pprint import pprint

con = MongoClient()
db = con.bilibili

"""
method: list users' places distribution and count
"""
def list_place():
    docs = db.user.aggregate([
        { '$group': { '_id': '$place',
                      'count': { '$sum' : 1 } } },
        { '$sort' : { 'count' : -1 } }
    ])
    show(docs)

#======= TODO LIST ======
#
# $aggregate sex
# $aggregate register_time
# $aggregate birthday
# $aggregate level
#
# $rank attetion
# $rank follower
# $rank playNum
# $rank danmaku
# $rank ratio - attention / follower
#
# $list fav
# $list subscribe
#
#========================

"""
method: print every doc inside
"""
def show(docs):
    for doc in docs:
        pprint(doc)

if __name__ == '__main__':
    list_place()

