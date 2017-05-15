# -*-coding:utf-8-*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import simplejson
import random

from public.mysqlpooldao import MysqlDao
from public.redispooldao import RedisDao

redis_key = 'dianping_comment:20161207_dianping_shop_id'
mysql_dao = MysqlDao()
redis_dao = RedisDao()


if __name__ == '__main__':
    # sql = 'SELECT `id`,`city_name`,`district_name`,`category_name`,`category`,`shop_name`,`shop_id`,`shop_url` FROM `20161207_dianping_shop_url` WHERE `category_name`="美食" AND `comment_tag_status`=0'
    sql = 'SELECT `id`,`city_name`,`district_name`,`category_name`,`category`,`shop_name`,`shop_id`,`shop_url` FROM `20161207_dianping_shop_url` WHERE  `id_status`=1'

    shop_lists =list(mysql_dao.execute(sql))
    random.shuffle(shop_lists)
    for shop_list in shop_lists:
        shop_list_json = simplejson.dumps(shop_list)
        redis_dao.rpush(redis_key, shop_list_json)
        print(shop_list_json)
    print('over')