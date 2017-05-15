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

redis_key = 'dianping_recommend:20170221_dianping_shop_list_url'

def get_recommend_food(id,target_url):
    print '****************************************'
    print target_url
    res = requests.get(target_url, headers=headers)
    if res.status_code == 200:
        code = 200
        req = res.json()
        recommend_foods = req['allDishes']
        Recommend_totoal_food = []
        for recommend_food in recommend_foods:
            recommend_food_names = recommend_food['dishTagName'].replace('"', '')
            if recommend_food_names:
                recommend_food_name = recommend_food_names
            recommend_food_nums = recommend_food['tagCount']
            if recommend_food_nums:
                recommend_food_num = recommend_food_nums
            recommend_total = "'" + recommend_food_name + "':'" + str(recommend_food_num) + "'"
            Recommend_totoal_food.append(recommend_total)
        recommend_total = ",".join(Recommend_totoal_food)
        recommend_food_show = '{' + recommend_total + '}'
        today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `recommend_food`="%s",`recommend_food_time`="%s",`status_code`="%s"  WHERE (`id`="%s")' % (recommend_food_show,
            today, code, id)
        print sql
        mysql_dao.execute(sql)
    elif res.status_code == 400:
        print u'target_url不完整'
        code = 400
        food_recommend = u'页面请求不到，无推荐菜'
        today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `recommend_food`="%s",`recommend_food_time`="%s",`status_code`= "%s" WHERE (`id`="%s")' % (
            food_recommend, today, code, id)
        print sql
        mysql_dao.execute(sql)



def get_recommend_food_url(id,shop_url):
    shopid = cityid = power = mainCategoryId = shoptype = shopCityId = shopName = ''
    try:
        time.sleep(0.5)
        res = requests.get(shop_url, headers=headers,timeout=5)
    except Exception as e:
        traceback.print_exc()
        print(e)
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

            powers = re.findall('power:(.*?),', req)
            if powers:
                power = powers[0].strip()

            mainCategoryIds = re.findall('mainCategoryId:(.*?),', req)
            if mainCategoryIds:
                mainCategoryId = mainCategoryIds[0].strip()

            shoptypes = re.findall('shopType:(.*?),', req)
            if shoptypes:
                shoptype = shoptypes[0].strip()

            shopCityIds = re.findall('shopCityId:(.*?),', req)
            if shopCityIds:
                shopCityId = shopCityIds[0].strip()

            shopNames = re.findall('shopName:(.*?),', req)
            if shopNames:
                shopName = shopNames[0].replace('"', '').strip()

            # print shopid,cityid,power,mainCategoryId,shoptype,shopCityId,shopName
            target_url = 'http://www.dianping.com/ajax/json/shopDynamic/shopTabs?shopId=' + shopid + '&cityId=' + cityid + '&shopName=' + shopName + '&power=' + power + '&mainCategoryId=' + mainCategoryId + '&shopType=' + shoptype + '&shopCityId=' + shopCityId
            # print target_url
            return target_url
    elif res.status_code == 404:
        print u"改页面已失效"
        code = 404
        food_recommend = u'页面失效，无推荐菜'
        today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `recommend_food`="%s",`recommend_food_time`="%s",`status_code`= "%s" WHERE (`id`="%s")' % (
            food_recommend, today, code, id)
        print sql
        mysql_dao.execute(sql)
        return code
    elif res.status_code == 402:
        print u"该页面不展示"
        code = 402
        food_recommend = u'页面不展示，无推荐菜'
        today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `recommend_food`="%s",`recommend_food_time`="%s",`status_code`= "%s" WHERE (`id`="%s")' % (
            food_recommend, today, code, id)
        print sql
        mysql_dao.execute(sql)
        return code


if __name__ == '__main__':
    while True:
        shop_list_json = redis_dao.lpop(redis_key)
        if shop_list_json is None:
            break
        shop_list = simplejson.loads(shop_list_json)
        id = shop_list[0]
        shop_url = shop_list[1]
        try:
            target_url = get_recommend_food_url(id,shop_url)
            if target_url <> 404 and target_url <> 402:
                try:
                    get_recommend_food(id, target_url)
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    continue
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue






