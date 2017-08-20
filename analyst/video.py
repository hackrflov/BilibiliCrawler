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

    @classmethod
    def list(self):
        list_str =  """\
type '$ python user.py [func name]' with func names from following list:
- find
- sort_by_aid
- sort_by_coins
- sort_by_danmaku
- sort_by_pubdate
- sort_by_favorate
- sort_by_reply
- count_by_tagname
- count_by_toptype\
"""
        print list_str

    def sort_by_aid(self):
        self.sort_by_key('aid')

    def sort_by_coins(self):
        self.sort_by_key('coins')

    def sort_by_danmaku(self):
        self.sort_by_key('danmaku')

    def sort_by_pubdate(self):
        self.sort_by_key('pubdate')

    def sort_by_favorate(self):
        self.sort_by_key('favorate')

    def sort_by_reply(self):
        self.sort_by_key('reply')

    def count_by_tagname(self):
        self.count_by_key('tagname')

    def count_by_toptype(self):
        self.count_by_key('toptype')

if __name__ == '__main__':
    video = Video()
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        getattr(video, func_name)()
    else:
        video.list()

