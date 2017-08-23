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

LOG_LEVEL = 'INFO'
#LOG_LEVEL = 'DEBUG'

# Disable cookies to avoid banned
COOKIES_ENABLED = False

# Obey robots.txt rules
#ROBOTSTXT_OBEY = True
ROBOTSTXT_OBEY = False

# Enable proxy
PROXY_ENABLED = False

# Max waiting time
DOWNLOAD_TIMEOUT = 3
# Retry many times since proxies often fail
#RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
#RETRY_HTTP_CODES = [302, 500, 503, 504, 400, 403, 408]

# No redirect
REDIRECT_ENABLED = False

# Speed up
CONCURRENT_ITEMS = 500
CONCURRENT_REQUESTS = 1028
CONCURRENT_REQUESTS_PER_DOMAIN = 100000
DNSCACHE_ENABLED = True

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
