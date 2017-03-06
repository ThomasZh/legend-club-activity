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


# vendor mp.weixin.qq.com
# {_id(vendor_id), content}
class vendor_hha_dao(singleton):
    __vendor_hha_collection = None;


    def __init__(self):
        if self.__vendor_hha_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__vendor_hha_collection = db.vendor_hha;
        else:
            logging.info("vendor_hha_collection has inited......");


    def create(self,json):
        self.__vendor_hha_collection.insert(json);
        logging.info("create __vendor_hha_collection success......");


    # _id = vendor_id
    def query_not_safe(self, _id):
        cursor = self.__vendor_hha_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    # _id = vendor_id
    def query(self, _id):
        data = self.query_not_safe(_id)
        if not data:
            data = {"_id":_id, "content":""}
        else:
            try:
                data['content']
            except:
                data['content'] = ''
        return data


    def update(self, json):
        _id = json["_id"];
        self.__vendor_hha_collection.update({"_id":_id},{"$set":json});
        logging.info("update __vendor_hha_collection success......")


    def delete(self, _id):
        self.__vendor_hha_collection.remove({"_id":_id});
        logging.info("delete __vendor_hha_collection success......");
