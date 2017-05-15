# -*- coding: utf-8 -*-


from public.mysqlpooldao import MysqlDao


mysql_dao = MysqlDao()
f = open('dianping_id.txt')
lines = f.readlines()
result = []
for line in lines:

    single_line = line.replace('"', '').replace('\r\n', '')
    # print single_line
    id = int(single_line)
    print id

    sql = 'UPDATE `20161207_dianping_shop_url` SET `id_status`="1" WHERE (`shop_id`="%s")' % id
    print sql
    mysql_dao.execute(sql)
