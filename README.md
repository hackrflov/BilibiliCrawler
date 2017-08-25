# BilibiliCrawler

## Overview
A powerful crawler with analyzing tools designed to dig out interesting data from bilibili.com

## Requirements
- Python 2.7+
- MongoDB 3.4+

## Install
> pip install -r requirements.txt

## How to crawl
## Get started
> python launch.py
You can crawl specific data, e.g. user
> python launch.py user
You can go further - start with certain number, e.g. aid
> python launch.py video 1234321
To fullly use your CPU, you can run multiple spider at the same time
> python launch.py user
> python launch.py video
> python launch.py danmaku

## How to analyze
> cd analyst
> python user.py
type functions showed within instruction
> python video.py sort_by_toptype
