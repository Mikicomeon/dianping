# -*-coding:utf-8-*-

import sys
import time
import simplejson
import traceback
import pickle
import os
from lxml import etree
from selenium import webdriver
from public.headers import Headers
from public.hero import Hero
from public.mysqlpooldao import MysqlDao
from public.redispooldao import RedisDao

file_path = os.path.dirname(os.path.abspath(__file__))
mysql_dao = MysqlDao()
redis_dao = RedisDao()
hero = Hero(file_path)

redis_key = 'dianping_comment:20161207_dianping_shop_url'
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

def get_comment_tag(city_name, district_name, category_name, category, shop_name, shop_id, shop_url):
    tags = []
    while True:
        # shop_url = 'http://www.dianping.com/shop/506354'
        headers = Headers.get_headers()
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap['phantomjs.page.customHeaders.Referer'] = headers['Referer']
        cap['phantomjs.page.settings.userAgent'] = headers['User-Agent']
        cap['phantomjs.page.settings.resourceTimeout'] = '1000'
        driver = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=cap)
        n = 1
        while 1:
            driver.get(shop_url)
            html = driver.page_source
            if html:
                break
            else:
                print 'sleep %s s' % n
                time.sleep(1 * n)
                n += 1
        # print html
        # time.sleep(1)
        selector = etree.HTML(html)
        tags = selector.xpath('//div[@id="comment"]/div[@id="summaryfilter-wrapper"]/div[@class="comment-condition J-comment-condition Fix"]/div[@class="content"]/span/a/text()')
        print shop_url
        # print tags
        # print html
        if len(tags) == 0:
            if u'您使用的IP访问网站过于频繁' in html:
                print(u'遇到5位验证码')
                hero.super_woman(shop_url)
                continue
            elif u'请输入下方图形验证码' in html:
                print(u'遇到4位验证码')
                hero.super_man(shop_url)
                continue
            else:
                print 'wu'

        else:
            new_tags = []
            for tag in tags:
                aa = tag.replace(')', '')
                # print aa
                bb = aa.split('(')
                new_tags.append(bb)
                # print bb
            tag_dict = dict(new_tags)
            comment_tag_json = simplejson.dumps(tag_dict, ensure_ascii=False)
            comment_tag_json = comment_tag_json
            # print type(comment_tag_json)
            # print comment_tag_json
            sql = "INSERT ignore INTO `20170221_dianping_comment_tag` (`city_name`, `district_name`, `category_name`, `category`, `shop_name`,`shop_id`, `shop_url`, `comment_tag_json`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (city_name, district_name, category_name, category, shop_name,shop_id, shop_url, comment_tag_json)
            print(sql)
            mysql_dao.execute(sql)
            time.sleep(0.5)
        break
    print tags
    return tags

if __name__ == '__main__':
    while True:
        shop_list_json = redis_dao.lpop(redis_key)
        # print 11111
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
        # print 2222
        try:
            tags = get_comment_tag(city_name, district_name, category_name, category, shop_name, shop_id, shop_url)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
        print tags
        if len(tags) == 0:
            sql = 'UPDATE `20161207_dianping_shop_url` SET `comment_tag_status`="2" WHERE (`id`="%s")' % list_id
        else:
            sql = 'UPDATE `20161207_dianping_shop_url` SET `comment_tag_status`="1" WHERE (`id`="%s")' % list_id
        print(sql)
        mysql_dao.execute(sql)