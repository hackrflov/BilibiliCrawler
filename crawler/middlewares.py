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

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.proxy_enabled = settings.get('PROXY_ENABLED')
        if self. proxy_enabled == True:
            self.fetch_proxies()

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
                    self.proxy_list[proxy] = random.choice([0,0.1])
            except Exception as e:
                log.error('Fetch proxies failed, msg is {msg}, error detail: {err}'.format(msg=msg,err=e))
        log.info('Proxy fetching is done, get {} proxies'.format(len(self.proxy_list)))

    def process_request(self, request, spider):
        if self.proxy_enabled == True:
            rand_i = random.choice(range(-1,1))
            od = OrderedDict(sorted(self.proxy_list.items(), key=lambda t: t[1], reverse=True))
            if 'retry_times' not in request.meta and rand_i == -1:  # not use proxy
                pass
            else:  # use random proxy
                proxy = od.keys()[rand_i]
                request.meta['proxy'] = proxy
                log.debug('Connect to {u} ... Using proxy <{p}>, {n} left'.format(u=request.url, p=proxy, n=len(self.proxy_list)))

    def process_exception(self, request, exception, spider):
        print 'Process exception'
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
                self.proxy_list[proxy] += 0.5 - used_time
                if self.proxy_list[proxy] < 0:
                    self.remove_one(proxy)
                    log.info('Connect to {u} ... Using {s} seconds, remove proxy <{p}>, {n} left'.format(u=request.url, s=used_time, p=proxy, n=len(self.proxy_list)))
                else:
                    log.info('Connect to {u} ... Using {s} seconds, proxy <{p}> score increase to {r}'.format(u=request.url, s=used_time, p=proxy, r=self.proxy_list[proxy]))
        elif response.status == 200:
            used_time = request.meta['download_latency']
            log.debug('Connect to {u} ... Using {s} seconds, without proxy'.format(u=request.url, s=used_time))
        return response

    """
    method: remove failed proxy from proxy list
    """
    def remove_one(self, proxy):
        if proxy in self.proxy_list:
            del self.proxy_list[proxy]
            if len(self.proxy_list) <= 10:
                self.fetch_proxies()

class BilibiliSpiderMiddleware(object):

    def process_spider_output(self, response, result, spider):
        try:
            for v in result:
                yield v
        except KeyError as e:
            yield None
        except Exception as e:
            log.error('Handle errors when parsing <{u}>, details: {e}'.format(u=response.url, e=e))
            yield response.request

