#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: middlewares.py
    Date: 08/11/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import random

from user_agents import USER_AGENTS

class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

