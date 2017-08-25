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
NEWSPIDER_MODULE = 'crawler.spiders'

# Custom MongoDB connection
MONGO_HOST = '127.0.0.1'  # set x.x.x.x for remote access
MONGO_DB = 'bilibili'  # default collection name
MONGO_USERNAME = 'bili_crawler'  # for auth
MONGO_PASSWORD = 'bilibili'  # for auth

LOG_LEVEL = 'INFO'
#LOG_LEVEL = 'DEBUG'

# Disable cookies to avoid banned
COOKIES_ENABLED = False

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Enable proxy
PROXY_ENABLED = False

# Max waiting time
DOWNLOAD_TIMEOUT = 5
# Retry on most error codes since proxies fail for different reasons
RETRY_TIMES = 2
RETRY_HTTP_CODES = [302, 500, 503, 504, 400, 403, 408]

# No redirect
REDIRECT_ENABLED = False

# Speed up
CONCURRENT_ITEMS = 1000
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 100000
DNSCACHE_ENABLED = True
RETRY_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'crawler.middlewares.RandomProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,

    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'crawler.middlewares.RandomUserAgentMiddleware': 543
}

# Configure item pipelines
ITEM_PIPELINES = {
    'crawler.pipelines.BilibiliPipeline': 300,
}

SPIDER_MIDDLEWARES = {
    'crawler.middlewares.BilibiliSpiderMiddleware': 200,
}
