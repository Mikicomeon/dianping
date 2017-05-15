# -*- coding: utf-8 -*-

import simplejson
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class JsonToSql():
    @staticmethod
    def json_to_sql(json):
        sql = simplejson.dumps(json).replace('\\', '\\\\').replace('"', '\\"')
        return sql
