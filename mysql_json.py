# -*-coding:utf-8-*-

import simplejson
from public.mysqlpooldao import MysqlDao

mysql_dao = MysqlDao()
sql = "select comment_tag_json FROM 20170221_dianping_comment_tag"
comment_tag = mysql_dao.execute(sql)
tags = comment_tag[0]
tag = tags[0]
tag_dic = simplejson.loads(tag)
print tag_dic
print type(tag_dic)
