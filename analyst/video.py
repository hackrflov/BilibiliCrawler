#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    File Name: video.py
    Date: 08/18/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import sys

from bili_util import BiliUtil
import numpy as np
from sklearn import linear_model, svm


class Video(BiliUtil):

    clt_name = 'video'

    def sort_by_aid(self, limit=10):
        self.sort_by_key('aid', int(limit))

    def sort_by_coin(self):
        self.sort_by_key('coin')

    def sort_by_view(self):
        self.sort_by_key('view')

    def sort_by_danmaku(self):
        self.sort_by_key('danmaku')

    def sort_by_pubdate(self):
        self.sort_by_key('pubdate')

    def sort_by_favorate(self):
        self.sort_by_key('favorate')

    def sort_by_reply(self):
        self.sort_by_key('reply')

    def count_by_typename(self):
        self.count_by_key('typename')

    def count_by_toptype(self):
        self.count_by_key('toptype')

    def count_by_aid_part(self):
        docs = self.db.video.aggregate([
            { '$project' : { 'id_part' : { '$floor' : { '$divide' : [ '$aid', 1000000 ] } } } },
            { '$group' : { '_id' : '$id_part', 'count' : { '$sum' : 1 } } },
            { '$sort' : { '_id' : 1 } }
        ])
        self.show(docs)

    """
    method: 按视频tag寻找发布该类视频的用户
    """
    def find_user_with_tag(self, tag):
        docs = self.db.video.aggregate([
            { '$match' : { 'tag' : tag } },
            #{ '$sample' : { 'size' : 100 } },
            { '$lookup' :
                { 'from' : 'user',
                  'localField' : 'mid',
                  'foreignField' : 'mid',
                  'as' : 'author'
                }
            },
            { '$limit' : 10 }
        ])
        self.show(docs)

    def find_by_tag(self, tag):
        self.find_by_field('tags', [tag])

    def join_with_user(self):
        docs = self.db[self.clt_name].aggregate([
            { '$sample' : { 'size' : 10 } },
            { '$lookup' :
                { 'from' : 'user',
                  'localField' : 'mid',
                  'foreignField' : 'mid',
                  'as' : 'author'
                }
            },
            { '$limit' : 10 }
        ])
        self.show(docs)

    #========== Machine Learning ==========#

    """
    method: Use linear regression to predict coin
    input @view: view amount
    input @fav: favorite amount
    input @reply: reply amount
    """
    def predict_coin(self, view, fav, reply):
        docs = self.db.video.find({},['view','coin','favorite','reply']).limit(10000)
        doc_list = [doc for doc in docs]
        data = np.array([ [ doc['view'],doc['favorite'], doc['reply'] ] for doc in doc_list])
        target = np.array([doc['coin'] for doc in doc_list])
        reg = linear_model.LinearRegression()
        reg.fit(data, target)
        print reg.coef_
        print reg.predict([[int(view), int(fav), int(reply)]])



if __name__ == '__main__':
    video = Video()
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        if len(sys.argv) >= 3:
            getattr(video, func_name)(*sys.argv[2:])
        else:
            getattr(video, func_name)()
    else:
        video.list()

