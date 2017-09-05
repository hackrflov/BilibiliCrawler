#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: settings.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

BOT_NAME = 'bilibili'

SPIDER_MODULES = ['crawler.spiders']

LOG_LEVEL = 'INFO'

# Custom MongoDB connection
MONGO_HOST = '127.0.0.1'  # set x.x.x.x for remote access
MONGO_DB = 'bilibili'  # default collection name
MONGO_USERNAME = 'bili_crawler'  # for auth
MONGO_PASSWORD = 'bilibili'  # for auth

#LOG_LEVEL = 'DEBUG'

# Disable cookies to avoid banned
COOKIES_ENABLED = False

# No redirect
REDIRECT_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'crawler.middlewares.RandomUserAgentMiddleware': 543
}

# Configure item pipelines
ITEM_PIPELINES = {
    'crawler.pipelines.BilibiliPipeline': 300,
}
