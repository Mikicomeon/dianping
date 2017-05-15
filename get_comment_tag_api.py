# -*- coding: utf-8 -*-
import sys
import os
import datetime
import requests
from lxml import etree
import simplejson
import traceback
from public.mysqlpooldao import MysqlDao
from public.headers import Headers
from public.redispooldao import RedisDao
from public.hero import Hero
import time

reload(sys)
sys.setdefaultencoding('utf-8')

file_path = os.path.dirname(os.path.abspath(__file__))
mysql_dao = MysqlDao()
redis_dao = RedisDao()
hero = Hero(file_path)
import re
from public.headers import Headers
headers = Headers.get_headers()

redis_key = 'dianping_comment:20161207_dianping_shop_id'

def get_comment_tag(city_name, district_name, category_name, category, shop_name, shop_id, target_url):
    # print target_url
    # target_url = 'http://www.dianping.com/ajax/json/shopDynamic/allReview?shopId=4557300&cityId=16&categoryURLName=food&power=5&cityEnName=wuhan&shopType=10'
    comment_total_tags = {}

    res = requests.get(target_url, headers=headers)
    if res.status_code == 200:
        # code = 200
        req = res.json()
        # print req
        if 'summarys' in req:
            comment_tags = req['summarys']
            # print comment_tags
            print type(comment_tags)
            if comment_tags == 'null':
                return comment_total_tags
            elif comment_tags is None:
                return comment_total_tags
            else:
                for comment_tag in comment_tags:
                    comment_tag_names = comment_tag['summaryString']
                    if comment_tag_names:
                        comment_tag_name = comment_tag_names
                    comment_tag_nums = comment_tag['summaryCount']
                    if comment_tag_nums:
                        comment_tag_num = comment_tag_nums

                    comment_total_tags[comment_tag_name] = comment_tag_num
                print comment_total_tags

                comment_tag_json = simplejson.dumps(comment_total_tags, ensure_ascii=False)
                # today = time.strftime('%Y-%m-%d')
                sql = "INSERT ignore INTO `20170221_dianping_comment_tag` (`city_name`, `district_name`, `category_name`, `category`, `shop_name`,`shop_id`, `shop_url`, `comment_tag_json`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (city_name, district_name, category_name, category, shop_name,shop_id, shop_url, comment_tag_json)
                print(sql)
                mysql_dao.execute(sql)
                time.sleep(0.5)
        else:
            return comment_total_tags
    print comment_total_tags
    return comment_total_tags

def get_comment_tag_url(list_id,shop_url):
    try:
        time.sleep(0.1)
        res = requests.get(shop_url, headers=headers,timeout=5)
    except Exception as e:
        traceback.print_exc()
        print(e)
    print res.status_code
    if res.status_code == 200:
        req = res.content
        if u'您使用的IP访问网站过于频繁' in req:
            print(u'遇到5位验证码')
            hero.super_woman(shop_url)

        elif u'请输入下方图形验证码' in req:
            print(u'遇到4位验证码')
            hero.super_man(shop_url)

        else:
            shopids = re.findall('shopId:(.*?),', req)
            if shopids:
                shopid = shopids[0].strip()

            cityids = re.findall('cityId:(.*?),', req)
            if cityids:
                cityid = cityids[0].strip()

            cityEnNames = re.findall('cityEnName:(.*?),', req)
            if cityEnNames:
                cityEnName = cityEnNames[0].strip().replace('"', '')

            categoryURLNames = re.findall('categoryURLName:(.*?),', req)
            if categoryURLNames:
                categoryURLName = categoryURLNames[0].strip().replace('"', '')

            shoptypes = re.findall('shopType:(.*?),', req)
            if shoptypes:
                shoptype = shoptypes[0].strip()

            powers = re.findall('power:(.*?),', req)
            if powers:
                power = powers[0].strip()


            # print shopid,cityid,power,shoptype,categoryURLName,cityEnName
            target_url = 'http://www.dianping.com/ajax/json/shopDynamic/allReview?shopId=' + shopid + '&cityId=' + cityid + '&categoryURLName=' + categoryURLName + '&power=' + power + '&cityEnName=' + cityEnName + '&shopType=' + shoptype
            # print target_url
            return target_url
    else:
        print res.status_code
        print u"改页面已失效"
        code = res.status_code
        # tag_comment = u'页面失效，无评论标签'
        # today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `comment_tag_status`="3" WHERE (`id`="%s")' % list_id
        print sql
        mysql_dao.execute(sql)
        return code





if __name__ == '__main__':
    while True:
        shop_list_json = redis_dao.lpop(redis_key)
        if shop_list_json is None:
            break
        shop_list = simplejson.loads(shop_list_json)
        list_id = shop_list[0]
        city_name = shop_list[1]
        district_name = shop_list[2]
        category_name = shop_list[3]
        category = shop_list[4]
        shop_name = shop_list[5]
        shop_id = shop_list[6]
        shop_url = shop_list[7]
        try:
            target_url = get_comment_tag_url(list_id,shop_url)
            print target_url
            if target_url <> 404 and target_url <> 402:
                try:
                    tags = get_comment_tag(city_name, district_name, category_name, category, shop_name, shop_id, target_url)
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                print tags
                if len(tags) == 0:
                    sql = 'UPDATE `20161207_dianping_shop_url` SET `comment_tag_status`="2" WHERE (`id`="%s")' % list_id
                else:
                    sql = 'UPDATE `20161207_dianping_shop_url` SET `comment_tag_status`="1" WHERE (`id`="%s")' % list_id
                print(sql)
                mysql_dao.execute(sql)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
