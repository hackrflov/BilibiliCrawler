#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: middlewares.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import re
import random
import json
import base64
import requests
from collections import OrderedDict
import logging
log = logging.getLogger('scrapy.proxy')

from user_agents import USER_AGENTS


class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

"""
Cloned and modified from
https://github.com/aivarsk/scrapy-proxies.git
"""
class RandomProxyMiddleware(object):

    def __init__(self, settings):
        self.proxy_list = {}  # format { proxy : score }
        self.RETRY_TIMES = settings.get('RETRY_TIMES')
        self.fetch_proxies()

    def fetch_proxies(self):
        log.info('Fetching proxy list...')
        # Thanks @fate0 for providing this awesome list
        url = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
        r = requests.get(url)
        data = r.text.split('\n')
        for msg in data:
            if msg == '':
                continue
            try:
                msg = json.loads(msg)
                proxy = '{_type}://{host}:{port}'.format(_type=msg['type'], host=msg['host'], port=msg['port'])
                if proxy not in self.proxy_list:
                    self.proxy_list[proxy] = 0
            except Exception as e:
                log.error('Fetch proxies failed, msg is {msg}, error detail: {err}'.format(msg=msg,err=e))
        log.info('Proxy fetching is done, get {} proxies'.format(len(self.proxy_list)))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # If contain force_proxy key or retry_times key, add proxy
        if 'force_proxy' in request.meta or 'retry_times' in request.meta:
            # choose proxy with highest score
            od = OrderedDict(sorted(self.proxy_list.items(), key=lambda t: t[1], reverse=True))
            proxy = od.keys()[0]

            request.meta['proxy'] = proxy  # set proxy
            self.proxy_list[proxy] -= 1  # score minus 1 after used
            log.debug('Connect to {u} ... Using proxy <{p}>, {n} left'.format(u=request.url, p=proxy, n=len(self.proxy_list)))

    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            self.remove_one(proxy)
            log.info('Failed to connect {u} ... Removing proxy <{p}>, {n} left, details: {d}'.format(u=request.url, p=proxy, n=len(self.proxy_list), d=exception))

    def process_response(self, request, response, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            if response.status != 200:
                self.remove_one(proxy)
                log.info('Failed to connect {u} ... Removing proxy <{p}>, {n} left, details: {d}'.format(u=request.url, p=proxy, n=len(self.proxy_list), d=response.status))
            else:
                used_time = request.meta['download_latency']
                self.proxy_list[proxy] += int(5/used_time)
                log.info('Connect to {u} ... Using {s} seconds, add proxy <{p}> score to {r}'.format(u=request.url, s=used_time, p=proxy, r=self.proxy_list[proxy]))
        return response

    """
    method: remove failed proxy from proxy list
    """
    def remove_one(self, proxy):
        if proxy in self.proxy_list:
            del self.proxy_list[proxy]
            self.update_pool()

    """
    method: check & update pool - keep usable
    """
    def update_pool(self):
        if len(self.proxy_list) <= 100:
            self.fetch_proxies()


class BilibiliSpiderMiddleware(object):

    def __init__(self):
        self.failed_urls = []

    def process_spider_output(self, response, result, spider):
        try:
            re = result.next()
        except Exception as e:
            if response.url in self.failed_urls:
                self.failed_urls.remove(response.url)
            else:  # retry once
                log.info('Handle errors when parsing <{u}>'.format(u=response.url))
                self.failed_urls.append(response.url)
            yield response.request
