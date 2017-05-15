#-*- coding:utf-8 -*-

import sys
import simplejson
from public.mysqlpooldao import MysqlDao
from public.redispooldao import RedisDao

redis_key = 'dianpingtest:20170104_dianping_shop_list_url'
mysql_dao = MysqlDao()
redis_dao = RedisDao()

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    sql = 'SELECT * FROM `20170104_dianping_shop_list_url` WHERE `status`=0'
    district_lists = mysql_dao.execute(sql)
    for district_list in district_lists:
        district_list_json = simplejson.dumps(district_list)
        redis_dao.rpush(redis_key,district_list_json)
        print district_list_json
