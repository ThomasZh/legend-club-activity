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


# vendor bonus options
# {'_id':'uuid', 'vendor_id':VENDOR_ID, 'account_id':'from_aplan', 'res_id':'activity_id',
#   'create_time':0, 'bonus':0, 'type':1/2/3}
# type=10 shared_activity +500
# type=20 shared_cert     +500
# type=30 buy_activity    -500
class bonus_dao(singleton):
    __bonus_collection = None;

    def __init__(self):
        if self.__bonus_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__bonus_collection = db.bonus;
        else:
            logging.info("bonus_dao has inited......");


    def create(self, json):
        self.__bonus_collection.insert(json);
        logging.info("create vendor bonus success......");


    # 非安全查询，用户在某种资源（活动）下获得的积分
    def query_not_safe_by_res(self, res_id, account_id, _type):
        cursor = self.__bonus_collection.find({"res_id":res_id, "account_id":account_id, "type":_type})
        data = None
        for i in cursor:
            data = i
        return data


    # 分页查询，用户在vendor下的积分
    def query_pagination_by_vendor(self, vendor_id, account_id, before, limit):
        cursor = self.__bonus_collection.find({
                "vendor_id":vendor_id,
                "account_id":account_id,
                "create_time":{"$lt":before}}).sort("create_time",-1).limit(limit);
        array = []
        for i in cursor:
            array.append(i)
        return array
