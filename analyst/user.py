#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File Name: user.py
    Date: 08/16/2017
    Author: hackrflov
    Email: hackrflov@gmail.com
    Python Version: 2.7
"""

import sys

from bili_util import BiliUtil

class User(BiliUtil):

    clt_name = 'user'

    def sort_by_playNum(self):
        self.sort_by_key('playNum')

    def sort_by_mid(self):
        self.sort_by_key('mid')

    def sort_by_attention(self):
        self.sort_by_key('attention')

    def sort_by_regtime(self):
        self.sort_by_key('regtime')

    def count_by_place(self):
        self.count_by_key('place')

    def count_by_sex(self):
        self.count_by_key('sex')

    def count_by_level(self):
        self.count_by_key('level')

    def count_by_nameplate(self):
        self.count_by_key('nameplate')

if __name__ == '__main__':
    user = User()
    if len(sys.argv) >= 2:
        func_name = sys.argv[1]
        getattr(user, func_name)()
    else:
        user.list()

