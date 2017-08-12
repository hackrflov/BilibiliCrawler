# -*- coding: utf-8 -*-

'''
    File name: items.py
    Author: hackrflov
    Date created: 8/11/2017
    Python version: 2.7
'''

import scrapy

class BilibiliItem(scrapy.Item):
    def fill(self, data):
        for key, value in data.iteritems():
            if key in self.fields:
                self[key] = value

"""
用户数据
数据源1: https://space.bilibili.com/ajax/member/GetInfo?mid={MID} - POST
数据源2: http://api.bilibili.com/cardrich?mid={MID}&type={TYPE}
"""
class UserItem(BilibiliItem):

    mid = scrapy.Field()  # ID
    name = scrapy.Field()  # 昵称
    approve = scrapy.Field()  # 是否认证
    sex = scrapy.Field()  # 性别
    face = scrapy.Field()  # 头像
    regtime = scrapy.Field()  # 注册时间
    place = scrapy.Field()  # 地区
    birthday = scrapy.Field()  # 生日
    sign = scrapy.Field()  # 签名
    description = scrapy.Field()  # 描述
    fans = scrapy.Field()  # 粉丝数
    attentions = scrapy.Field()  # 关注列表
    attention = scrapy.Field()  # 关注数
    level_info = scrapy.Field()  # 等级
    nameplate = scrapy.Field()  # 勋章

    favs = scrapy.Field()  # 收藏视频

    coins = scrapy.Field()  # 硬币数
    playNum = scrapy.Field()  # 播放数

"""
视频数据
数据源1: http://m.bilibili.com/video/av{AID}.html
数据源2: https://api.bilibili.com/x/web-interface/archive/stat?aid={AID}
"""
class VideoItem(BilibiliItem):

    aid = scrapy.Field()  # AV号
    pubdate = scrapy.Field()  # 日期
    title = scrapy.Field()  # 标题
    description = scrapy.Field()  # 描述
    mid = scrapy.Field()  # 作者ID
    writer = scrapy.Field()  # 作者昵称
    duration = scrapy.Field()  # 时长
    toptype = scrapy.Field()  # 分区
    tags = scrapy.Field()  # 标签
    typeid = scrapy.Field()  # 类别ID
    typename = scrapy.Field()  # 类别
    totalpage = scrapy.Field()  # 页数
    litpic = scrapy.Field()  # 封面

    view = scrapy.Field()  # 浏览数
    danmaku = scrapy.Field()  # 弹幕数
    reply = scrapy.Field()  # 评论数
    favorite = scrapy.Field()  # 收藏数
    coin = scrapy.Field()  # 硬币数
    share = scrapy.Field()  # 分享数
    now_rank = scrapy.Field()  # 当前排名
    his_rank = scrapy.Field()  # 最高排名
    copyright = scrapy.Field()  # 版权


"""
弹幕数据
数据源: https://comment.bilibili.com/{CID}.xml
"""
class DanmakuItem(BilibiliItem):

    cid = scrapy.Field()  # 视频ID
    playTime = scrapy.Field()  # 时间
    mode = scrapy.Field()  # 模式
    fontsize = scrapy.Field()  # 字体大小
    color = scrapy.Field()  # 颜色
    timestamp = scrapy.Field()  # 时间戳
    pool = scrapy.Field()  # 弹幕池
    hashID = scrapy.Field()  # 用户ID
    uid = scrapy.Field()  # 弹幕ID
    msg = scrapy.Field()  # 文本


