# -*- coding: utf-8 -*-

import sys
import requests
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.city import City
from public.headers import Headers

reload(sys)
sys.setdefaultencoding('utf-8')
mysql_dao = MysqlDao()


def get_district_info(city_singlename,city_trueurl):
    headers = Headers.get_headers()
    res = requests.get(city_trueurl,headers=headers)
    print res
    wb_data = res.content
    selector = etree.HTML(wb_data)
    district_names = selector.xpath('.//*[@id="region-nav"]/a')
    category_name = selector.xpath('.//div[@class="bread J_bread"]/span/a/span[@itemprop="title"]/text()')
    if category_name:
        category_name = category_name[0]
    for district_name in district_names:
        district_namename = district_name.xpath('span/text()')
        if district_namename:
            district_namename = district_namename[0]
            district_url = district_name.xpath('@href')
            if district_url:
                district_url = 'http://www.dianping.com'+district_url[0]
            # print district_namename,district_url,category_name
            sql = (
                'INSERT IGNORE INTO `20170104_dianping_shop_list_url`'
                '(`city_name`,`district_name`,`category_name`,`url`)'
                'VALUES ("%s","%s","%s","%s")'
                ) % (city_singlename,district_namename,category_name,district_url)
            print sql
            mysql_dao.execute(sql)


if __name__ == '__main__':
    city_list = City.city_list
    headers = Headers.get_headers()
    url = 'http://www.dianping.com/citylist'
    res = requests.get(url,headers=headers)
    print res
    wb_data = res.content
    selector = etree.HTML(wb_data)
    cities = selector.xpath('.//*[@id="divPY"]/li/div/a')
    for city in cities:
        city_singlename = city.xpath('descendant::text()')
        if city_singlename:
            city_singlename = city_singlename[0]
            for (city_name, city_id) in city_list.items():
                if city_singlename in city_name:
                    city_trueurl = 'http://www.dianping.com/search/category/{}/20/g0r0'.format(city_id)
                    print city_singlename,city_trueurl
                    get_district_info(city_singlename,city_trueurl)



