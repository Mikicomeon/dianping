# -*- coding: utf-8 -*-


import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import simplejson

from public.mysqlpooldao import MysqlDao
from public.redispooldao import RedisDao

redis_key = 'dianping_recommend:20170221_dianping_shop_list_url'
mysql_dao = MysqlDao()
redis_dao = RedisDao()

if __name__ == '__main__':
    sql = "SELECT `id`,`shop_id` FROM `20161207_dianping_shop_url` WHERE new_recommend_food = ''"
    shop_lists = mysql_dao.execute(sql)
    for shop_list in shop_lists:
        shop_list_json = simplejson.dumps(shop_list)
        redis_dao.rpush(redis_key, shop_list_json)
        print(shop_list_json)
