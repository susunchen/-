# -*- coding: utf-8 -*-
SERVER_PORT = 8999
DEBUG = False
SQLALCHEMY_ECHO = False
AUTH_COOKIE_NAME = "mooc_food"

'''
过滤URL
'''
IGNORE_URLS = {
    "^/user/login",
    "^/api", "^/qrcode","^/production","^/cabint"
}


API_IGNORE_URLS = [
    "^/api"
]
IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]


PAGE_SIZE = 50
PAGE_DISPLAY = 10



STATUS_MAPPING = {
    "1":"正常",
    "0":"已删除"
}

CABINT_STATUS_MAPPING = {
    "1":"空置",
    "0":"使用中"
}

MINA_APP = {
    'appid' :'wx701dd190df5db6b9',
    'appkey' : 'd619bdeaf5f0377fa7b615cda660587e'


}

UPLOAD = {
    'ext':[ 'jpg','gif','bmp','jpeg','png' ],
    'prefix_path':'/web/static/upload/',
    'prefix_url':'/static/upload/'
}
APP = {
    'domain':'http://47.111.15.243:8999'
}
PAY_STATUS_MAPPING = {
    "1":"已支付",
    "-8":"待支付",
    "0":"已关闭"
}

PAY_STATUS_DISPLAY_MAPPING = {
    "0":"订单关闭",
    "1":"待评价",
    "3":"已完成",
    "2":"已完成",
    "-8":"待支付",
    "-7":"支付完成代配送确认",
    "-6":"配送确认代生产",
    "-5":"生产完成代入柜",
    "-4":"入柜成功代收取",
    "-3":"收取成功配送中",
    "-2":"已经送达,用户待确认",
    "4":"评价完成",
}