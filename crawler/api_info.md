'''
B站 api接口列表
'''

# 可用app_key列表
appkey_list = [
    '12737ff7776f1ade',
    '8e9fc618fbd41e28',
    '03fc8eb101b091fb' # 待测试
]

# 用户信息
'http://api.bilibili.com/cardrich?mid=122541'
'https://space.bilibili.com/ajax/member/GetInfo'

# 用户收藏视频
'https://api.bilibili.com/x/v2/fav/folder?vmid=15281064'
'https://api.bilibili.com/x/v2/fav/video?vmid=15276139&fid=68244294&page=2'

# 用户订阅番剧
'https://space.bilibili.com/ajax/Bangumi/getList?mid=30312292&page=2'

# 用户发布视频列表
'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=30312292&page=1&pagesize=25'

# 用户投过硬币视频列表
'https://space.bilibili.com/ajax/member/getCoinVideos?mid=30312292'

# 用户代表作
'https://space.bilibili.com/ajax/masterpiece/get?mid=30312292&guest=1'

# 用户置顶视频
'https://space.bilibili.com/ajax/top/showTop?mid=30312292&guest=1'


########
# 视频
########

# 视频信息
'https://api.bilibili.com/view?appkey={APPKEY}&id={ID}&type={TYPE}'.format(APPKEY='8e9fc618fbd41e28',ID='11672651',TYPE='json')
'http://m.bilibili.com/video/av12825132.html'

# 首页信息
'http://api.bilibili.com/x/web-interface/dynamic/index?jsonp=jsonp'

# 视频CID
'http://www.bilibili.com/widget/getPageList?aid=12894919'

# 弹幕文本
'http://comment.bilibili.com/21185110.xml'

# 弹幕日期
'http://comment.bilibili.com/rolldate,21185110'

# 历史弹幕
'http://comment.bilibili.com/dmroll,1501776000,21185110'

# 推荐列表
'http://comment.bilibili.com/recommendnew,12894919'

# 视频标签
'http://api.bilibili.com/x/tag/archive/tags?aid=12894919'

# 视频数据
'http://api.bilibili.com/x/web-interface/archive/stat?aid=12894919'

# 评论数据 (sort: 0 全部评论 2 按照热度排序)
'http://api.bilibili.com/x/v2/reply?pn=2&type=1&oid=12894919&sort=0'

# TODO
# http://interface.bilibili.tv/playurl?aid=&appkey=
形式:http://interface.bilibili.tv/playurl?platform=android&cid=’从view接口取得的cid‘&appkey=’你的appkey‘&quality=‘ 清晰度1,2’&type=mp4


###########
#  番剧
###########
https://bangumi.bilibili.com/jsonp/seasoninfo/{sid}.ver?

# Emoji列表
'http://api.bilibili.com/x/v2/reply/web/emojis'
