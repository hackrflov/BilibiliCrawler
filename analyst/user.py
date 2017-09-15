#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: user.py
    Date: 08/16/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import sys

import random
from bili_util import BiliUtil

class User(BiliUtil):

    clt_name = 'user'

    def sort_by_fans(self):
        self.sort_by_key('fans')

    def sort_by_attention(self):
        self.sort_by_key('attention')

    def sort_by_mid(self, limit=10):
        self.sort_by_key('mid', int(limit))

    def sort_by_attention(self):
        self.sort_by_key('attention')

    def sort_by_regtime(self):
        self.sort_by_key('regtime')

    def sort_by_season(self):
        self.sort_by_key('season')

    def sort_by_fav(self):
        self.sort_by_key('fav')

    def count_by_place(self):
        self.count_by_key('place')

    def count_by_sex(self):
        self.count_by_key('sex')

    """
    method: 按视频tag寻找收藏该类视频的用户
    """

    def count_by_level(self):
        self.count_by_key('level')

    def count_by_nameplate(self):
        self.count_by_key('nameplate')

    def count_by_year(self):
        docs = self.db[self.clt_name].aggregate([
            { '$match' : { 'birthday' : { '$ne' : '' } } },
            { '$project' : { 'birthday' : { '$substrBytes' : [ '$birthday', 0, 4 ] } } },
            { '$group': { '_id': '$birthday',
                          'count': { '$sum' : 1 } } },
            { '$sort' : { 'count' : -1 } }
        ])
        self.show(docs)

    # Twelve constellations
    def count_by_sign(self):
        docs = self.db[self.clt_name].aggregate([
            { '$match' : { 'birthday' : { '$ne' : '' } } },
            { '$project' : { 'birthday' : { '$substrBytes' : [ '$birthday', 5, 9 ] } } },
            { '$group': { '_id': '$birthday',
                          'count': { '$sum' : 1 } } },
            { '$sort' : { 'count' : -1 } }
        ])
        signs = {}
        for doc in docs:
            birthday = doc['_id']
            if birthday in ['','01-01','00-00']:
                continue
            month = int(birthday[0:2])
            day = int(birthday[-2:])
            n = ['摩羯座','水瓶座','双鱼座','白羊座','金牛座','双子座','巨蟹座','狮子座','处女座','天秤座','天蝎座','射手座']
            d = [(1,20),(2,19),(3,21),(4,21),(5,21),(6,22),(7,23),(8,23),(9,23),(10,23),(11,23),(12,23)]
            sign = n[len(filter(lambda y:y<=(month,day), d))%12]
            if sign in signs:
                signs[sign] += doc['count']
            else:
                signs[sign] = 0
        for (key, value) in sorted(signs.items(),key=lambda t: t[1], reverse=True):
            print key, value

    def join_with_video(self):
        docs = self.db[self.clt_name].aggregate([
            { '$match' : { 'nameplate' : { '$exists' : 1 } } },
            { '$sample' : { 'size' : 10 } },
            { '$lookup' :
                { 'from' : 'video',
                  'localField' : 'mid',
                  'foreignField' : 'mid',
                  'as' : 'author'
                }
            },
            { '$limit' : 10 }
        ])
        self.show(docs)

    def favorite_videos(self, mid=0):
        if mid == 0:
            mid = random.randint(0,10000)
        docs = self.db[self.clt_name].aggregate([
            { '$match' : { 'mid' : mid } },
            { '$project' : { 'tag' : 1, 'mid' : 1, 'name' : 1, 'favorite' : 1 } },
            { '$unwind' : '$favorite' },
            { '$lookup' :
                { 'from' : 'video',
                  'localField' : 'favorite.id',
                  'foreignField' : 'aid',
                  'as' : 'favs'
                }
            },
            { '$limit' : 2000 }
        ])
        self.show(docs)

    def favorite_size(self):
        docs = self.db.user.aggregate([
            { '$match' : { 'favorite' : { '$exists' : True, '$not' : { '$size' : 0 } } } },
            { '$project' : { 'size' : { '$size' : '$favorite' } } },
            { '$group' : { '_id' : '$size', 'count' : { '$sum' : 1 } } },
            { '$sort' : { '_id' : -1 } }
        ])
        self.show(docs)

    """
    method: comprehensively analyze user type
    """
    def user_type(self, mid=0):
        if mid == 0:
            mid = random.randint(10000000,10300000)
        # Favorite videos toptype
        print '====== User {} basic info ======'.format(mid)
        self.show(self.db.user.find({'mid':mid}))

        print '\n====== Favorite videos ======'
        docs = self.db.user.aggregate([
            { '$match' : { 'mid' : mid } },
            { '$unwind' : '$favorite' },
            { '$lookup' :
                { 'from' : 'video',
                  'localField' : 'favorite.id',
                  'foreignField' : 'aid',
                  'as' : 'video'
                }
            },
            { '$unwind' : '$video' },
            { '$match' : { 'video.typename' : { '$exists' : 1 } } },
            { '$project' : { 'toptype' : '$video.toptype', 'typename' : '$video.typename' } },
            { '$group' : { '_id' : { 'toptype' : '$toptype', 'typename' : '$typename' }, 'count' : { '$sum' : 1 } } },
            { '$sort' : { 'count' : -1 } },
        ])
        self.show(docs)

        print '\n====== Submit videos ======'
        docs = self.db.user.aggregate([
            { '$match' : { 'mid' : mid } },
            { '$lookup' :
                { 'from' : 'video',
                  'localField' : 'mid',
                  'foreignField' : 'mid',
                  'as' : 'video'
                }
            },
            { '$unwind' : '$video' },
            { '$match' : { 'video.typename' : { '$exists' : 1 } } },
            { '$project' : { 'toptype' : '$video.toptype', 'typename' : '$video.typename' } },
            { '$group' : { '_id' : { 'toptype' : '$toptype', 'typename' : '$typename' }, 'count' : { '$sum' : 1 } } },
            { '$sort' : { 'count' : -1 } },
        ])
        self.show(docs)


if __name__ == '__main__':
    user = User()
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        if len(sys.argv) == 3:
            getattr(user, func_name)(sys.argv[2])
        elif len(sys.argv) >= 4:
            v = sys.argv[3]
            try:
                v = int(v)
            except:
                pass
            getattr(user, func_name)(sys.argv[2],v)
        else:
            getattr(user, func_name)()
    else:
        user.list()

