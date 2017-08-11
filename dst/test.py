from pymongo import MongoClient
import requests
import pdb

if __name__ == '__main__':
    proxies = {
        'http': 'http://113.58.232.203:808'
    }
    requests.get('http://api.bilibili.com/cardrich?mid=15281558', proxies=proxies)
    print requests.status_code
    print requests.json()
