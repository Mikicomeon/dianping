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

reload(sys)
sys.setdefaultencoding('utf-8')

file_path = os.path.dirname(os.path.abspath(__file__))
mysql_dao = MysqlDao()
redis_dao = RedisDao()
hero = Hero(file_path)

redis_key = 'dianpingtest:20170104_dianping_shop_list_url'


def get_last_page(url):
    last_page = 1
    try:
        headers = Headers.get_headers()
        req = requests.get(url, headers=headers, timeout=5)
        if req.status_code == 200:
            html = req.content
            selector = etree.HTML(html)
            last_pages = selector.xpath('//div[@class="page"]/a[last()-1]/text()')
            if len(last_pages) > 0:
                # print len(last_pages)
                last_page = int(last_pages[0])
                # print last_page
    except Exception as e:
        traceback.print_exc()
        print(e)
    return last_page


def get_shop_info(url, last_page, city_name, district_name, category_name, list_id):
    # print url,last_page,city_name,district_name,category_name,list_id
    page = last_page
    while True:
        if page <= 0:
            break
        target_url = url + 'p' + str(page)
        print(target_url)
        headers = Headers.get_headers()
        try:
            req = requests.get(target_url, headers=headers, timeout=5)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
        if req.status_code == 200 or req.status_code == 403:
            html = req.content
            if u'您使用的IP访问网站过于频繁' in html:
                print(u'遇到5位验证码')
                hero.super_woman(target_url)
                continue
            elif u'请输入下方图形验证码' in html:
                print(u'遇到4位验证码')
                hero.super_man(target_url)
                continue
            else:
                selector = etree.HTML(html)
                shop = selector.xpath('//div[@id="shop-all-list"]/ul/li')
                for s in shop:
                    img_url = shop_name = shop_url = shop_id = region_name  = star = address = chun1 = chun2 = chun3 = type = review_url =''
                    consumption = comment_num = 0
                    # 店铺名称
                    shop_names = s.xpath('div[@class="txt"]/div[@class="tit"]/a[1]/h4/text()')
                    if len(shop_names) > 0:
                        shop_name = shop_names[0].replace('"', '').replace(' ', '')

                    # 商户url
                    shop_urls = s.xpath('div[@class="txt"]/div[@class="tit"]/a/@href')
                    if len(shop_urls) > 0:
                        shop_url = 'http://www.dianping.com' + shop_urls[0]
                        shop_id = shop_url.replace('http://www.dianping.com/shop/', '')
                        review_url = shop_url + '/review_all'

                    # 商圈名称
                    region_names = s.xpath('div[@class="txt"]/div[@class="tag-addr"]/a[2]/span/text()')
                    if len(region_names) > 0:
                        region_name = region_names[0].replace('"', '').replace(' ', '')

                    # 店铺图 ###########################################################
                    img_urls = s.xpath('div[@class="pic"]/a[@target="_blank"]/img/@data-src')
                    for i in img_urls:
                        img_url = i if img_url == '' else img_url + '|' + i
                        # if img_url == '':
                        #     img_url = i
                        # else:
                        #     img_url = img_url + '|' + i

                    # 人均
                    consumptions = s.xpath('div[@class="txt"]/div[@class="comment"]/a[@class="mean-price"]/b/text()')
                    if len(consumptions) > 0:
                        consumption = consumptions[0].replace('¥', '').replace('￥', '')
                        consumption = consumption.replace('\r\n', '').replace(' ', '')
                        if consumption == '':
                            consumption = 0
                    # 评星
                    stars = s.xpath('div[@class="txt"]/div[@class="comment"]/span/@title')
                    if len(stars) > 0:
                        star = stars[0]
                    #地址
                    addresses = s.xpath('div[@class="txt"]/div[@class="tag-addr"]/span[@class="addr"]/text()')
                    if len(addresses) > 0:
                        address = addresses[0]

                    # 评分
                    chuns1 = s.xpath('div[@class="txt"]/span/span[1]/b/text()')
                    if len(chuns1) > 0:
                        chun1 = chuns1[0]
                    chuns2 = s.xpath('div[@class="txt"]/span/span[2]/b/text()')
                    if len(chuns2) > 0:
                        chun2 = chuns2[0]
                    chuns3 = s.xpath('div[@class="txt"]/span/span[3]/b/text()')
                    if len(chuns3) > 0:
                        chun3 = chuns3[0]
                    tag = chun1 + "|" + chun2 + "|" + chun3

                    # 评论数
                    comment_nums = s.xpath('div[@class="txt"]/div[@class="comment"]/a[@class="review-num"]/b/text()')
                    if len(comment_nums) > 0:
                        comment_num = comment_nums[0].replace(')', '').replace('(', '')
                    #  类型
                    types = s.xpath(
                        'div[@class="txt"]/div[@class="tag-addr"]/a[1]/span/text()')
                    if len(types) > 0:
                        type = types[0]

                    crawl_date = datetime.date.today()
                    # print city_name, district_name, region_name, category_name, shop_id, shop_name, consumption,star, tag,comment_num, shop_url, img_url, crawl_date
                    values = (
                        city_name, district_name, region_name, category_name, shop_id, shop_name, consumption,
                        star, tag,
                        comment_num, shop_url, img_url, crawl_date,address,type,review_url)

                    sql = (
                              'INSERT ignore INTO'
                              ' `20170104_dianping_shop_url`'
                              ' (`city_name`, `district_name`, `region_name`, `category_name`, `shop_id`,'
                              ' `shop_name`, `consumption`, `star`, `tag`, `comment_num`,'
                              ' `shop_url`, `img`, `crawl_date`,`address`,`type`,`review_url`)'
                              ' VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s",'
                              ' "%s", "%s", "%s", "%s", "%s", "%s","%s","%s","%s")'
                          ) % values
                    print(sql)
                    try:
                        mysql_dao.execute(sql)
                    except:
                        print('error')
        else:
            print(req.status_code)
        page = page - 1


if __name__ == '__main__':
    while True:
        district_list_json = redis_dao.lpop(redis_key)
        if district_list_json is None:
            break
        district_list = simplejson.loads(district_list_json)
        list_id = district_list[0]
        city_name = district_list[1]
        district_name = district_list[2]
        category_name = district_list[3]
        list_url = district_list[4]
        print list_id,city_name,district_name,category_name,list_url
        last_page = get_last_page(list_url)
        try:
            get_shop_info(list_url, last_page, city_name, district_name, category_name, list_id)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue
        sql = 'UPDATE `20170104_dianping_shop_list_url` SET `status`="1" WHERE (`id`="%s")' % list_id
        print(sql)
        mysql_dao.execute(sql)
