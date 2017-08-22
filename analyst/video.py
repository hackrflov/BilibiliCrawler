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

"""
method: list videos which contain certain tag, i.e. BGM, 镇站之宝, 万恶之源
"""
def hot_tag():
    tag = '万恶之源'
    docs = db.video.find( { 'tags' : { '$in' : [tag] } } )#.sort({ 'favorates' : -1 })
    show(docs)

class Video(BiliUtil):

    clt_name = 'video'

    def sort_by_aid(self):
        self.sort_by_key('aid')

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

if __name__ == '__main__':
    video = Video()
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        if len(sys.argv) == 3:
            getattr(video, func_name)(sys.argv[2])
        elif len(sys.argv) >= 4:
            getattr(video, func_name)(sys.argv[2],sys.argv[3])
        else:
            getattr(video, func_name)()
    else:
        video.list()

