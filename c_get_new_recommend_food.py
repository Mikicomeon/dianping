# -*-coding:utf-8-*-

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
# headers = Headers.get_headers()
redis_key = 'dianping_recommend:20170221_dianping_shop_list_url'

def get_new_recommend_food(id, dianping_id):
    url = 'https://apimeishi.meituan.com/meishi/dppoi/v1/poi/featureMenu/' + str(dianping_id) + '?uuid=AC74481FD031D92051AF2BC341375AABE4281994CF70C1E01392D1D83DED1437&utm_source=AppStore&utm_term=9.1.8&utm_content=AC74481FD031D92051AF2BC341375AABE4281994CF70C1E01392D1D83DED1437&version_name=9.1.8&userid=1174951013&needfilter=true&utm_medium=iphone&movieBundleVersion=100&utm_campaign=Adianping-novaB%28null%29H0&__reqTraceID=3309E777-C144-4A2F-AB5B-40360505EAE3&page=0&ci=0&msid=80A7C3C4-979D-4991-9390-06446663E24F2017-03-06-15-28432'
    print url
    res = requests.get(url)
    if res.status_code == 200:
        code = '200'
        html = res.json()
        # print html
        new_recommend_food = []
        data = []
        name = price = img = count = ''
        if 'data' in html:
            data = html['data']
            # print data
            for c in data:
                recommend_food = {}
                name = c['name'].replace("'", '')
                price = c['price']
                img = c['imgUrl']
                count = c['recCount']
                recommend_food['name'] = name
                recommend_food['price'] = price
                recommend_food['img'] = img
                recommend_food['count'] = count

                # print recommend_food
                new_recommend_food.append(recommend_food)
            # print new_recommend_food
            new_recommend_food_json = simplejson.dumps(new_recommend_food, ensure_ascii=False)
            print new_recommend_food_json
            # print new_recommend_food
            today = time.strftime('%Y-%m-%d')
            sql = "UPDATE `20161207_dianping_shop_url` SET `new_recommend_food`='%s',`recommend_food_time`='%s', `status_code`= '%s' WHERE (`id`='%s')" % (new_recommend_food_json,
                today, code, id)
            print sql
            mysql_dao.execute(sql)
    elif res.status_code == 400:
        print u'target_url不完整'
        code = 400
        food_recommend = u'页面请求不到，无推荐菜'
        today = time.strftime('%Y-%m-%d')
        sql = 'UPDATE `20161207_dianping_shop_url` SET `new_recommend_food`="%s",`recommend_food_time`="%s",`status_code`= "%s" WHERE (`id`="%s")' % (
            food_recommend, today, code, id)
        print sql
        mysql_dao.execute(sql)

if __name__ == '__main__':
    while True:
        shop_list_json = redis_dao.lpop(redis_key)
        if shop_list_json is None:
            break
        shop_list = simplejson.loads(shop_list_json)
        id = shop_list[0]
        dianping_id = shop_list[1]
        try:

            get_new_recommend_food(id, dianping_id)

        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
    print 'over'
