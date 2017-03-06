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


from xml.etree import ElementTree

#def print_node(node):
#    '''打印结点基本信息'''
#    print "=============================================="
#    print "node.attrib:%s" % node.attrib
#    if node.attrib.has_key("age") > 0 :
#        print "node.attrib['age']:%s" % node.attrib['age']
#    print "node.tag:%s" % node.tag
#    print "node.text:%s" % node.text


#<xml>
# <return_code><![CDATA[SUCCESS]]></return_code>\n
# <return_msg><![CDATA[OK]]></return_msg>\n
# <appid><![CDATA[wxaa328c83d3132bfb]]></appid>\n
# <mch_id><![CDATA[1340430801]]></mch_id>\n
# <nonce_str><![CDATA[lYeiS0ISsMakYRGu]]></nonce_str>\n
# <sign><![CDATA[4A80190EFDDA2B22A46535BF77CC3C7D]]></sign>\n
# <result_code><![CDATA[SUCCESS]]></result_code>\n
# <prepay_id><![CDATA[wx2016051011051929643983670302291635]]></prepay_id>\n
# <trade_type><![CDATA[JSAPI]]></trade_type>\n
#</xml>
def parseWxOrderReturn(xml):
    root = ElementTree.fromstring(xml)

    order_return = {}

    lst_node = root.getiterator("return_code")
    for node in lst_node:
        #print_node(node)
        order_return['return_code'] = node.text

    lst_node = root.getiterator("return_msg")
    for node in lst_node:
        #print_node(node)
        order_return['return_msg'] = node.text

    lst_node = root.getiterator("appid")
    for node in lst_node:
        #print_node(node)
        order_return['appid'] = node.text

    lst_node = root.getiterator("mch_id")
    for node in lst_node:
        #print_node(node)
        order_return['mch_id'] = node.text

    lst_node = root.getiterator("nonce_str")
    for node in lst_node:
        #print_node(node)
        order_return['nonce_str'] = node.text

    lst_node = root.getiterator("sign")
    for node in lst_node:
        #print_node(node)
        order_return['sign'] = node.text

    lst_node = root.getiterator("result_code")
    for node in lst_node:
        #print_node(node)
        order_return['result_code'] = node.text

    lst_node = root.getiterator("prepay_id")
    for node in lst_node:
        #print_node(node)
        order_return['prepay_id'] = node.text

    lst_node = root.getiterator("trade_type")
    for node in lst_node:
        #print_node(node)
        order_return['trade_type'] = node.text

    return order_return

#<xml>
# <appid><![CDATA[wxaa328c83d3132bfb]]></appid>\n
# <attach><![CDATA[Aplan]]></attach>\n
# <bank_type><![CDATA[CFT]]></bank_type>\n
# <cash_fee><![CDATA[1]]></cash_fee>\n
# <fee_type><![CDATA[CNY]]></fee_type>\n
# <is_subscribe><![CDATA[Y]]></is_subscribe>\n
# <mch_id><![CDATA[1340430801]]></mch_id>\n
# <nonce_str><![CDATA[jOhHjqDfx9VQGmU]]></nonce_str>\n
# <openid><![CDATA[oy0Kxt7zNpZFEldQmHwFF-RSLNV0]]></openid>\n
# <out_trade_no><![CDATA[e358738e30fe11e69a7e00163e007b3e]]></out_trade_no>\n
# <result_code><![CDATA[SUCCESS]]></result_code>\n
# <return_code><![CDATA[SUCCESS]]></return_code>\n
# <sign><![CDATA[6291D73149D05F09D18C432E986C4DEB]]></sign>\n
# <time_end><![CDATA[20160613083651]]></time_end>\n
# <total_fee>1</total_fee>\n
# <trade_type><![CDATA[JSAPI]]></trade_type>\n
# <transaction_id><![CDATA[4007652001201606137183943151]]></transaction_id>\n
#</xml>
def parseWxPayReturn(xml):
    root = ElementTree.fromstring(xml)

    pay_return = {}

    lst_node = root.getiterator("return_code")
    for node in lst_node:
        #print_node(node)
        pay_return['return_code'] = node.text

    lst_node = root.getiterator("return_msg")
    for node in lst_node:
        #print_node(node)
        pay_return['return_msg'] = node.text

    lst_node = root.getiterator("appid")
    for node in lst_node:
        #print_node(node)
        pay_return['appid'] = node.text

    lst_node = root.getiterator("mch_id")
    for node in lst_node:
        #print_node(node)
        pay_return['mch_id'] = node.text

    lst_node = root.getiterator("nonce_str")
    for node in lst_node:
        #print_node(node)
        pay_return['nonce_str'] = node.text

    lst_node = root.getiterator("sign")
    for node in lst_node:
        #print_node(node)
        pay_return['sign'] = node.text

    lst_node = root.getiterator("result_code")
    for node in lst_node:
        #print_node(node)
        pay_return['result_code'] = node.text

    lst_node = root.getiterator("prepay_id")
    for node in lst_node:
        #print_node(node)
        pay_return['prepay_id'] = node.text

    lst_node = root.getiterator("trade_type")
    for node in lst_node:
        #print_node(node)
        pay_return['trade_type'] = node.text

    lst_node = root.getiterator("time_end")
    for node in lst_node:
        #print_node(node)
        pay_return['time_end'] = node.text

    lst_node = root.getiterator("total_fee")
    for node in lst_node:
        #print_node(node)
        pay_return['total_fee'] = node.text

    lst_node = root.getiterator("transaction_id")
    for node in lst_node:
        #print_node(node)
        pay_return['transaction_id'] = node.text

    lst_node = root.getiterator("out_trade_no")
    for node in lst_node:
        #print_node(node)
        pay_return['out_trade_no'] = node.text

    return pay_return
