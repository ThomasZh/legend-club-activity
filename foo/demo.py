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

import tornado.web
import logging
from dao import budge_num_dao
from global_const import VENDOR_ID


# /demo/index
class DemoIndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('demo/index.html')


# /demo/blank
class DemoBlankHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('demo/blank.html')


# /demo/regexp-params/[a-z]*[0-9]*
class DemoRegexpParamsHandler(tornado.web.RequestHandler):
    def get(self):
        # Sanitize argument lists:
        uri = self.request.uri
        logging.info("got uri %r", uri)
        array = uri.split('/')
        param = None
        for s in array:
            param = s
            logging.info("got param %r", s)

        self.render('demo/regexp-params.html', param=param)


# /demo/games/<string:game_id>/code/<int:code>
class DemoGamesCodeHandler(tornado.web.RequestHandler):
    def get(self, game_id, code):
        logging.info("got game_id %r", game_id)
        logging.info("got code %r", code)

        self.render('demo/regexp-params.html', param=game_id+'-'+code)


# /demo/mongodb/init
class DemoMongodbInitHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info("got VENDOR_ID %r", VENDOR_ID)
        _budge_num = budge_num_dao.budge_num_dao().query(VENDOR_ID);
        logging.info("got application %r", _budge_num['application'])
        logging.info("got order %r", _budge_num['order'])
        logging.info("got total %r", _budge_num['total'])
        self.render('demo/blank.html')


# /demo/mongodb/init
class DemoAlipayHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('demo/alipay.html')
