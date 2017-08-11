# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import random
import json
import base64
import logging

log = logging.getLogger('scrapy.proxy')

from user_agents import USER_AGENTS


class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

"""
Clone and modify from
https://github.com/aivarsk/scrapy-proxies.git
"""
class RandomProxyMiddleware(object):

    def __init__(self, settings):
        self.proxy_list = settings.get('PROXY_LIST')
        self.RETRY_TIMES = settings.get('RETRY_TIMES')
        if self.proxy_list is None:
            raise KeyError('PROXY_LIST setting is missing')

        self.fetch_proxies()

    def fetch_proxies(self):
        fin = open(self.proxy_list)
        self.proxies = {}
        for line in fin.readlines():
            parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line.strip())
            if not parts:
                continue

            # Cut trailing @
            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[parts.group(1) + parts.group(3)] = user_pass
        fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            if request.meta["exception"] is False:
                return
        request.meta["exception"] = False
        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')

        proxy_address = random.choice(list(self.proxies.keys()))
        proxy_user_pass = self.proxies[proxy_address]

        if proxy_user_pass:
            request.meta['proxy'] = proxy_address
            basic_auth = 'Basic ' + base64.b64encode(proxy_user_pass.encode()).decode()
            request.headers['Proxy-Authorization'] = basic_auth
        else:
            log.debug('Proxy user pass not found')
        log.info('Using proxy <%s>, %d proxies left' % (
                proxy_address, len(self.proxies)))

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        proxy = request.meta['proxy']
        try:
            del self.proxies[proxy]
        except KeyError:
            pass
        request.meta["exception"] = True
        log.info('Removing failed proxy <%s>, %d proxies left' % (
                proxy, len(self.proxies)))

        if len(self.proxies) <= 10:
            self.fetch_proxies()

    def process_response(self, request, response, spider):
        if 'retry_times' in request.meta and \
                request.meta['retry_times'] >= self.RETRY_TIMES and \
                'proxy' in request.meta:        # try do not use proxy
            del request.meta['proxy']
            print response.status, request.url, request.meta
            return request
        else:
            return response

