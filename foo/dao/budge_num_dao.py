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
from global_const import MONGO_HOST, MONGO_PORT, MONGO_USR, MONGO_PWD, MONGO_DB


# 一个vendor有且只有一个budge_num
# {"application":0, "order":0, "total":0}
class budge_num_dao(singleton):
    __budge_num_collection = None;

    def __init__(self):
        if self.__budge_num_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__budge_num_collection = db.budge_num;
        else:
            logging.info("budge_num_dao has inited......");


    # 未做安全保护的查询
    # 私有函数，内部使用
    # _id = vender_id
    def __query_not_safe(self, _id):
        cursor = self.__budge_num_collection.find({"_id": _id})
        data = None
        for i in cursor:
            data = i
        return data


    # 查询时，如为空，则初始化所有数据为0
    # _id = vender_id
    def query(self, _id):
        data = self.__query_not_safe(_id)
        if not data:
            data = {"application":0, "order":0, "voucher_order":0, "total":0}
        else:
            try:
                data['application']
            except:
                data['application'] = 0
            try:
                data['order']
            except:
                data['order'] = 0
            try:
                data['voucher_order']
            except:
                data['voucher_order'] = 0
            data['total'] = data['application'] + data['order'] + data['voucher_order']
        return data


    # _id = vender_id
    def update(self, json):
        _id = json["_id"];
        data = self.__query_not_safe(_id)
        if not data:
            self.__budge_num_collection.insert(json);
        else:
            self.__budge_num_collection.update({"_id":_id}, {"$set":json});
        logging.info("update budge_num success......");
