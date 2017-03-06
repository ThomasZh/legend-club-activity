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
# {_id(vendor_id), wx_app_id, wx_app_secret, wx_mch_id, wx_mch_key, wx_qrcode, create_time}
class vendor_wx_dao(singleton):
    __vendor_wx_collection = None;


    def __init__(self):
        if self.__vendor_wx_collection is None:
            conn = pymongo.MongoClient(MONGO_HOST, MONGO_PORT);
            db = conn[MONGO_DB];
            db.authenticate(MONGO_USR, MONGO_PWD);
            self.__vendor_wx_collection = db.vendor_wx;
        else:
            logging.info("insurance_template_dao has inited......");


    def create(self,json):
        self.__vendor_wx_collection.insert(json);
        logging.info("create vendor_wx success......");


    # _id = vendor_id
    def query_not_safe(self, _id):
        cursor = self.__vendor_wx_collection.find({"_id":_id})
        data = None
        for i in cursor:
            data = i
        return data


    # _id = vendor_id
    def query(self, _id):
        data = self.query_not_safe(_id)
        if not data:
            data = {"_id":_id, "wx_app_id":"", "wx_app_secret":"", "wx_mch_id":"", "wx_mch_key":"", "wx_qrcode":""}
        else:
            try:
                data['wx_app_id']
            except:
                data['wx_app_id'] = ''
            try:
                data['wx_app_secret']
            except:
                data['wx_app_secret'] = ''
            try:
                data['wx_mch_id']
            except:
                data['wx_mch_id'] = ''
            try:
                data['wx_mch_key']
            except:
                data['wx_mch_key'] = ''
            try:
                data['wx_qrcode']
            except:
                data['wx_qrcode'] = ''
        return data


    def update(self, json):
        _id = json["_id"];
        self.__vendor_wx_collection.update({"_id":_id},{"$set":json});
        logging.info("update vendor_wx success......")


    def delete(self, _id):
        self.__vendor_wx_collection.remove({"_id":_id});
        logging.info("delete vendor_wx success......");
