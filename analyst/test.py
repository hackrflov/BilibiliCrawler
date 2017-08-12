# -*- coding: utf-8 -*-

'''
    File name: test.py
    Author: hackrflov
    Date created: 8/11/2017
    Python version: 2.7
'''

import pdb

from pymongo import MongoClient

def show(cursor):
    for doc in cursor:
        print doc

def fetch_data():
    # cur = db.user.find()
    # cur = db.user.find({ 'sex': '男' })
    # cur = db.runCommand({ 'distinct': 'user', 'key': 'place' })
    cur = db.user.aggregate([
        { '$project': { 'place': 1 } },
        { '$group': { '_id': '$place', 'count': { '$sum' : 1 } } },
        { '$sort' : { 'count' :-1 }}
    ])
    return cur

def fetch_and_calc():
    for user in db.user.find():
#        pdb.set_trace()
        mid = user['mid']
        # find his video
        for video in db.video.find({'mid': mid}):
            print '######'
            print user
            print video
            print '######'

if __name__ == '__main__':
    client = MongoClient()
    db = client.bilibili
#    cur = fetch_data()
#    show(cur)
    fetch_and_calc()
