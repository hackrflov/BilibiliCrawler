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

    def __init__(self):
        # Uncomment to use proxy
        # self.fetch_proxies()
        pass

    def fetch_proxies(self):
        self.proxy_list = {} # format { proxy : score }
        log.info('Fetching proxy list...')
        # Thanks @fate0 for providing this awesome list
        url = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
        r = requests.get(url)
        data = r.text.split('\n')
        for msg in data[:-1]:
            try:
                msg = json.loads(msg)
                proxy = '{_type}://{host}:{port}'.format(_type=msg['type'], host=msg['host'], port=msg['port'])
                if proxy not in self.proxy_list:
                    self.proxy_list[proxy] = 0
            except Exception as e:
                log.error('Fetch proxies failed, msg is {msg}, error detail: {err}'.format(msg=msg,err=e))
        log.info('Proxy fetching is done, get {} proxies'.format(len(self.proxy_list)))

    def process_request(self, request, spider):
        # If contain force_proxy key or retry_times key, add proxy
        if 'force_proxy' in request.meta or 'retry_times' in request.meta:
            # choose proxy with highest score
            od = OrderedDict(sorted(self.proxy_list.items(), key=lambda t: t[1], reverse=True))
            proxy = od.keys()[0]
            self.proxy_list[proxy] -= 0.5  # score minus 0.5 after use
            request.meta['proxy'] = proxy  # set proxy
            log.debug('Connect to {u} ... Using proxy <{p}>, {n} left'.format(u=request.url, p=proxy, n=len(self.proxy_list)))
            # check proxy pool
            if od.values()[0] < 0:  # all proxies are slow
                self.fetch_proxies()

    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            self.remove_one(proxy)
            log.info('Failed to connect {u} ... Removing proxy <{p}>, {n} left, details: {d}'.format(u=request.url, p=proxy, n=len(self.proxy_list), d=exception))

    def process_response(self, request, response, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            if response.status not in [200,400,401,402,403,404,407]:
                self.remove_one(proxy)   # remove bad proxy
                log.info('Failed to connect {u} ... Removing proxy <{p}>, {n} left, details: {d}'.format(u=request.url, p=proxy, n=len(self.proxy_list), d=response.status))
            elif proxy in self.proxy_list:
                used_time = request.meta['download_latency']
                self.proxy_list[proxy] += 6 - min(10, int(used_time/0.05))
                log.info('Connect to {u} ... Using {s} seconds, add proxy <{p}> score to {r}'.format(u=request.url, s=used_time, p=proxy, r=self.proxy_list[proxy]))
        elif response.status == 200:
            used_time = request.meta['download_latency']
            log.info('Connect to {u} ... Using {s} seconds'.format(u=request.url, s=used_time))
        return response

    """
    method: remove failed proxy from proxy list
    """
    def remove_one(self, proxy):
        if proxy in self.proxy_list:
            del self.proxy_list[proxy]

class BilibiliSpiderMiddleware(object):

    def __init__(self):
        self.failed_urls = []

    def process_spider_output(self, response, result, spider):
        try:
            for v in result:
                yield v
        except Exception as error:
            if response.url in self.failed_urls:
                self.failed_urls.remove(response.url)
            else:  # retry once
                log.info('Handle errors when parsing <{u}>, details: {e}'.format(u=response.url, e=error))
                if response.url not in self.failed_urls:
                    self.failed_urls.append(response.url)
            yield response.request

