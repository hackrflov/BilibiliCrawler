#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: middlewares.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import time
import json
import random
import requests
import threading
import logging
log = logging.getLogger('scrapy.middleware')

from datetime import datetime, timedelta

from user_agents import USER_AGENTS

class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

class RandomProxyMiddleware(object):

    def __init__(self):
        self.last_time = datetime.now()  # last time using local ip to access
        self.fetch_finished = False
        t = threading.Thread(target = self.get_proxies)
        t.daemon = True
        t.start()

    def get_proxies(self):
        while True:
            r = requests.get('http://183.131.144.70:5000/')
            data = json.loads(r.text)['data']
            self.proxy_list = ['http://{}'.format(ip) for ip in data]
            self.fetch_finished = True
            # 每隔5分钟刷新一次
            time.sleep(300)

    def process_request(self, request, spider):
        if 'enable_proxy' in request.meta and self.fetch_finished and 'retry_times' not in request.meta:
            request.meta['proxy'] = random.choice(self.proxy_list)
            request.meta['download_timeout'] = st.PROXY_TIMEOUT
            log.debug('Connect to {u}, meta details: {m}'.format(u=request.url, m=request.meta))

    def process_exception(self, request, exception, spider):
        log.debug('in pro_exp:{u}, {m} , error details: {e}'.format(u=request.url, m=request.meta, e=exception))
        if 'enable_proxy' in request.meta and self.fetch_finished:
            if 'proxy' in request.meta:
                del request.meta['proxy']
                del request.meta['download_timeout']

    def process_response(self, request, response, spider):
        if response.status != 200:
            log.debug('in pro_res: status = {s}, {u}, {m}, {b}'.format(s=response.status, u=response.url, m=request.meta, b=response.body[:1000]))
            if 'proxy' in request.meta:
                del request.meta['proxy']
                del request.meta['download_timeout']
        else:
            log.debug('in pro_res: status=200, proxy={p}, used {s}s'.format(p=request.meta.get('proxy'), s=request.meta['download_latency']))
        return response
