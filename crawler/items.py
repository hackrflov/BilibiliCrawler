#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: items.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import scrapy

class BilibiliItem(scrapy.Item):

    def __init__(self, data={}, item_type='default'):
        super(BilibiliItem, self).__init__()
        self.fill(data)
        self._type = item_type   # default: upsert ; append: add into array

    def fill(self, data):
        for key, value in data.items():
            if value and key in self.fields:
                self[key] = value

"""
Data source1: https://space.bilibili.com/ajax/member/GetInfo?mid={MID} - POST
Data source2: http://api.bilibili.com/cardrich?mid={MID}&type={TYPE}
Data source3: http://m.bilibili.com/space/{MID}
Data source4: https://app.bilibili.com/x/v2/space?vmid={MID}&build=1&ps=1
"""
class UserItem(BilibiliItem):

    mid = scrapy.Field()  # ID
    name = scrapy.Field()  # 昵称
    approve = scrapy.Field()  # 是否认证
    description = scrapy.Field()  # 官方描述
    sex = scrapy.Field()  # 性别
    regtime = scrapy.Field()  # 注册时间
    birthday = scrapy.Field()  # 生日
    place = scrapy.Field()  # 地区
    fans = scrapy.Field()  # 粉丝数
    attention = scrapy.Field()  # 关注数
    level = scrapy.Field()  # 等级
    nameplate = scrapy.Field()  # 勋章
    vip = scrapy.Field()  # VIP
    article = scrapy.Field() # 投稿数

    setting = scrapy.Field() # 隐私设置
    live = scrapy.Field() # 直播间
    elec = scrapy.Field()  # 充电数
    folder = scrapy.Field()  # 收藏夹  https://api.bilibili.com/x/v2/fav/folder?vmid={} -> data -> fid [no-limit]
    favorite = scrapy.Field() # 收藏视频  https://api.bilibili.com/x/v2/fav/video?vmid={}&fid={} -> data -> archives -> aid [30/page]
    attentions = scrapy.Field()  # 关注列表  http://api.bilibili.com/cardrich?mid={} -> data -> card -> attentions [no-limit]
    community = scrapy.Field()  # 兴趣圈  https://app.bilibili.com/x/v2/space/community?vmid={} -> data -> item -> id [20/page]
    bangumi = scrapy.Field()  # 订阅番剧  https://app.bilibili.com/x/v2/space/bangumi?vmid={} -> data -> item -> param [20/page]
    tag = scrapy.Field()  # 订阅标签  https://space.bilibili.com/ajax/tags/getSubList?mid={} -> data -> tags -> name [no-limit]
    game = scrapy.Field() # 游戏

    # setting properties
    _unique_key = 'mid'
    _db_name = 'user'


"""
Data source1: http://m.bilibili.com/video/av{AID}.html
Data source2: https://api.bilibili.com/x/web-interface/archive/stat?aid={AID}
"""
class VideoItem(BilibiliItem):

    aid = scrapy.Field()  # AV号
    cid = scrapy.Field()  # 视频号
    pubdate = scrapy.Field()  # 日期
    title = scrapy.Field()  # 标题
    # description = scrapy.Field()  # 描述
    mid = scrapy.Field()  # 作者ID
    # writer = scrapy.Field()  # 作者昵称
    duration = scrapy.Field()  # 时长
    toptype = scrapy.Field()  # 分区
    tags = scrapy.Field()  # 标签
    typeid = scrapy.Field()  # 类别ID
    typename = scrapy.Field()  # 类别
    totalpage = scrapy.Field()  # 页数
    # litpic = scrapy.Field()  # 封面

    view = scrapy.Field()  # 浏览数
    danmaku = scrapy.Field()  # 弹幕数
    reply = scrapy.Field()  # 评论数
    favorite = scrapy.Field()  # 收藏数
    coin = scrapy.Field()  # 硬币数
    share = scrapy.Field()  # 分享数
    # now_rank = scrapy.Field()  # 当前排名
    his_rank = scrapy.Field()  # 最高排名
    copyright = scrapy.Field()  # 版权

    # setting properties
    _unique_key = 'aid'
    _db_name = 'video'


"""
Data source: https://comment.bilibili.com/{CID}.xml
"""
class DanmakuItem(BilibiliItem):

    cid = scrapy.Field()  # 视频ID
    playTime = scrapy.Field()  # 时间
    #mode = scrapy.Field()  # 模式
    #fontsize = scrapy.Field()  # 字体大小
    #color = scrapy.Field()  # 颜色
    timestamp = scrapy.Field()  # 时间戳
    #pool = scrapy.Field()  # 弹幕池
    #hashID = scrapy.Field()  # 用户ID
    uid = scrapy.Field()  # 弹幕ID
    msg = scrapy.Field()  # 文本

    # setting properties
    _unique_key = 'uid'
    _db_name = 'danmaku'


"""
Data source: http://bangumi.bilibili.com/jsonp/seasoninfo/{sid}.ver?
"""
class BangumiItem(BilibiliItem):

    sid = scrapy.Field()  # 番剧ID
    bangumi_id =  scrapy.Field()  # 系列ID
    title = scrapy.Field()  # 标题
    total_count = scrapy.Field()  # 共几话
    area = scrapy.Field()  # 国家
    tags = scrapy.Field()  # 标签
    brief = scrapy.Field()  # 简介
    pub_time = scrapy.Field()  # 开播时间
    play_count = scrapy.Field()  # 播放数
    favorites = scrapy.Field()  # 追番数
    danmaku_count = scrapy.Field()  # 弹幕数

    # setting properties
    _unique_key = 'sid'
    _db_name = 'bangumi'

