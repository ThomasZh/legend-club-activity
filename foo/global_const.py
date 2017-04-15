#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# thomas@time2box.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

STP = "123.56.105.78"
API_HOST = "127.0.0.1"
API_PORT = "8009"
# STP = "127.0.0.1:8082"
# bike-forever club
LEAGUE_ID = "f24794c7e1d511e68c0aa45e60efbf2d"
CLUB_ID = "702c87d4f73111e69a3c00163e023e51"
VENDOR_ID = "b9f1ffe612aa11e6a4f6a45e60efbf2d"
# mongodb
MONGO_HOST = "123.56.165.59"
MONGO_PORT = 3717
MONGO_DB = "legend-club"
MONGO_USR = "club"
MONGO_PWD = "uWx-nJs-8J3-vA9"


# WX_APP_ID = "wxf7ed1dbed18855bf"
# WX_APP_SECRET = "3a030120ec5db2c637736f1d3af91248"
# WX_MCH_ID = "1349315001"
# WX_MCH_KEY = "97cc3d5e4c0311e6a93fa45e60efbf2d"
# WX_NOTIFY_DOMAIN = "https://www.bike-forever.com"

# A计划（红）
WX_APP_ID = "wxaa328c83d3132bfb"
WX_APP_SECRET = "32bbf99a46d80b24bae81e8c8558c42f"
WX_MCH_ID = "1340430801"
WX_MCH_KEY = "b9f1ffe612aa11e6a4f6a45e60efbf2d"
# WX_NOTIFY_DOMAIN = "http://planc2c.com"
WX_NOTIFY_DOMAIN="http://7x24hs.com"

# A计划服务号（绿）
# WX_APP_ID = "wx445c952b09d519ec"
# WX_APP_SECRET = "35b6fcfd5af1d13440b39fe4ab1b327f"
# WX_MCH_ID = "1399535402"
# WX_MCH_KEY = "Q1YywLGITEmEmj0d227Ms2e0hQe610JZ"
# WX_NOTIFY_DOMAIN="http://7x24hs.com"


QRCODE_CREATE_URL = "http://qrcode.7x24hs.com/api/qrcode"

TOKEN_EXPIRES_IN = 7200 # 2hours
DEFAULT_USER_ID = "00000000000000000000000000000000"
DEFAULT_USER_AVATAR = "http://tripc2c-person-face.b0.upaiyun.com/default/user.png"
DEFAULT_USER_NICKNAME = "匿名"

# status: 10=Draft, 20=Recruit
ACTIVITY_STATUS_CANCELED = 5          # 已取消
ACTIVITY_STATUS_DRAFT = 10            # 草稿箱
ACTIVITY_STATUS_RECRUIT = 20          # 招募中
ACTIVITY_STATUS_DOING = 30            # 活动中
ACTIVITY_STATUS_COMPLETED = 40        # 已完成
ACTIVITY_STATUS_POP = 50              # 热门


# order status
ORDER_STATUS_BF_INIT = 10             # 在bike-forever系统中初始化创建成功
ORDER_STATUS_WECHAT_UNIFIED_SUCCESS = 20      # 微信统一下单返回成功
ORDER_STATUS_WECHAT_UNIFIED_FAILED = 21      # 微信统一下单返回失败
ORDER_STATUS_WECHAT_PAY_SUCCESS = 30  # 调用微信支付接口，返回成功
ORDER_STATUS_WECHAT_PAY_FAILED = 31   # 调用微信支付接口，返回失败
ORDER_STATUS_BF_APPLY_REFUND = 40     # 在bike-forever系统中，申请退款
ORDER_STATUS_BF_REFUND_SUCCESS = 41   # 在bike-forever系统中，申请退款
ORDER_STATUS_BF_APPLY = 50            # 报名信息填写，提交成功
ORDER_STATUS_BF_DELIVER = 60          # 活动完毕，服务交付
ORDER_STATUS_BF_COMMENT = 70          # 活动完毕，评价完毕


# bonus type
BONUS_TYPE_SHAERD_ACTIVITY = 10     # 分享活动，获得积分
BONUS_TYPE_SHAERD_CRET = 20         # 分享证书，获得积分
BONUS_TYPE_BUY_ACTIVITY = 30        # 使用积分，购买活动


# voucher status
VOUCHER_STATUS_NOT_USED = 0         # 未使用
VOUCHER_STATUS_USED = 10            # 已使用


#page size
PAGE_SIZE_LIMIT = 20

GUEST_CLUB_ID = '00000000000000000000000000000000'


API_DOMAIN="http://7x24hs.com"
