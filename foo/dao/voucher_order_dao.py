# !/usr/bin/env python
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
from global_const import MONGO_HOST, MONGO_PORT, MONGO_USR, MONGO_PWD, MONGO_DB


#order options
# {
#  "_id":uuid,
#  "account_id": uuid,
#  "create_time": 0, "last_update_time": 0,
#  "status": 10,
#  "pay_type": "wxpay",
#  "voucher_id": uuid,
#  "total_price": 0, #整数, 转换为分
#  "applicant_num": 0, #购买数量
#  "voucher_price" : 100, #单价
#  "voucher_amount" :500, #面值
#  "vendor_id":uuid
# }
class voucher_order_dao(singleton):
    __voucher_order_collection = None;

    def __init__(self):
        if self.__voucher_order_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__voucher_order_collection = db.voucher_order;
        else:
            logging.info("voucher_order_dao has inited......");


    #voucher order options
    def create(self, json):
        self.__voucher_order_collection.insert(json);
        logging.info("create voucher order success......");


    def delete(self, _id):
        self.__voucher_order_collection.remove({"_id":_id});
        logging.info("delete voucher order success......");


    def update(self, json):
            _id = json["_id"];
            self.__voucher_order_collection.update({"_id":_id},{"$set":json});
            logging.info("update voucher order success......");


    def query(self, _id):
        cursor = self.__voucher_order_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data

    def count_not_review_by_vendor(self, vendor_id):
        return self.__voucher_order_collection.count({"vendor_id":vendor_id,"review":False})

    def query_by_account(self, voucher_id, account_id):
        cursor = self.__voucher_order_collection.find({
                "voucher_id":voucher_id,
                "account_id":account_id}).sort("create_time",-1)
        array = []
        for i in cursor:
            array.append(i)
        return array


    def query_pagination_by_vendor(self, vendor_id, before, limit):
            cursor = self.__voucher_order_collection.find({
                    "vendor_id":vendor_id,
                    "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
            array = []
            for i in cursor:
                array.append(i)
            return array


    def query_pagination_by_account(self, account_id, before, limit):
        cursor = self.__voucher_order_collection.find({
                "account_id":account_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array

    def query_pagination_by_vendor_account(self, vendor_id, account_id, before, limit):
        cursor = self.__voucher_order_collection.find({
                "vendor_id":vendor_id,
                "account_id":account_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array
