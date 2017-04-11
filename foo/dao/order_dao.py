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

import logging
import pymongo
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from comm import singleton
from global_const import MONGO_HOST, MONGO_PORT, MONGO_USR, MONGO_PWD, MONGO_DB, GUEST_CLUB_ID


#order options
# {
#  "_id":uuid,
#  "activity_id": uuid,
#  "account_id": uuid,
#  "create_time": 0, "last_update_time": 0,
#  "review": False,
#  "status": 10,
#  "pay_type": "wxpay",
#  "total_amount": 0, #整数, 转换为分
#  "applicant_num": 0, #购买数量
#  "ext_fees": [{"_id":uuid, "name":name, "fee":0}], #数组
#  "insurances": [{"_id":uuid, "name":name, "fee":0}], #数组
#  "vouchers": [{"_id":uuid, "fee":0}], #数组
#  "bonus": 0, #整数, 转换为分
#  "vendor_id":uuid
# }
class order_dao(singleton):
    __order_collection = None;

    def __init__(self):
        if self.__order_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__order_collection = db.order;
        else:
            logging.info("order_dao has inited......");


    #order options
    def create(self, json):
        self.__order_collection.insert(json);
        logging.info("create order success......");


    def query(self, _id):
        cursor = self.__order_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    def query_by_activity(self, activity_id):
        cursor = self.__order_collection.find({"activity_id":activity_id}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_by_account(self, activity_id, account_id):
        cursor = self.__order_collection.find({
                "activity_id":activity_id,
                "account_id":account_id}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array


    def count_not_review_by_vendor(self, vendor_id):
        return self.__order_collection.count({"vendor_id":vendor_id,"review":False})


    def update(self, json):
        _id = json["_id"];
        self.__order_collection.update({"_id":_id},{"$set":json});
        logging.info("update order success......");


    def query_pagination_by_vendor(self, vendor_id, before, limit):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array

    # 我的活动 别人订单
    def query_pagination_by_vendor_notme(self, vendor_id, before, limit):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "guest_club_id":{"$ne":vendor_id},
                "guest_club_id":{"$ne":GUEST_CLUB_ID},
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array

    # 别人活动我的订单
    def query_pagination_by_vendor_me(self, vendor_id, before, limit):
        cursor = self.__order_collection.find({
                "vendor_id":{"$ne":vendor_id},
                "guest_club_id":vendor_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_pagination_by_account(self, account_id, before, limit):
        cursor = self.__order_collection.find({
                "account_id":account_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_pagination_by_vendor_account(self, vendor_id, account_id, before, limit):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "account_id":account_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array


    def delete(self, _id):
        self.__order_collection.remove({"_id":_id});
        logging.info("delete order success......");

    def query_by_order_keys(self, vendor_id, order_keys_value):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "_id":{'$regex':order_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_title_keys(self, vendor_id, title_keys_value):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "activity_title":{'$regex':title_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_nickname_keys(self, vendor_id, nickname_keys_value):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "account_nickname":{'$regex':nickname_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_by_time_keys(self, vendor_id, begin_keys_value, end_keys_value):
        cursor = self.__order_collection.find({
                "vendor_id":vendor_id,
                "create_time":{'$gt':begin_keys_value,'$lt':end_keys_value}}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array
