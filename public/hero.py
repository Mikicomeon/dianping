# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from public.ruokuai import RuoKuai
from public.config import Config
from PIL import Image, ImageEnhance


class Hero(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def super_woman(self, target_url):
        print('super_woman')
        super_woman_driver = webdriver.PhantomJS(executable_path=r'/root/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        super_woman_driver.implicitly_wait(2)
        super_woman_driver.get(target_url)
        time.sleep(1)
        super_woman_driver.get_screenshot_as_file(self.file_path + '/code/v5.jpg')
        im = Image.open(self.file_path + '/code/v5.jpg')
        box = (8, 128, 128, 164)
        region = im.crop(box)
        region.save(self.file_path + "/code/v5_deal.jpg")
        print(super_woman_driver.page_source)
        if u'验证码' in super_woman_driver.page_source:
            button = super_woman_driver.find_element_by_xpath('//input[@type="submit"]')
            input = super_woman_driver.find_element_by_name('vode')
            rc = RuoKuai(Config.ruokuai_name, Config.ruokuai_pswd, Config.ruokuai_soft_id, Config.ruokuai_soft_key)
            im = open(self.file_path + '/code/v5_deal.jpg', 'rb').read()
            code = rc.rk_create(im, '3050')
            print(code)
            code_text = code['Result']
            print(code_text)
            input.send_keys(code_text)
            from selenium.webdriver import ActionChains
            actions = ActionChains(super_woman_driver)
            actions.move_to_element(button)
            actions.click(button)
            actions.perform()
            time.sleep(5)
            # button.click()
            # driver.implicitly_wait(10)
        super_woman_driver.quit()
        print('sleep50')
        time.sleep(50)

    def super_man(self, target_url):
        print('super_man')
        super_man_driver = webdriver.PhantomJS(executable_path=r'/root/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        super_man_driver.implicitly_wait(1)
        super_man_driver.get(target_url)
        time.sleep(0.1)
        super_man_driver.get_screenshot_as_file(self.file_path + '/code/v4.jpg')
        print(super_man_driver.page_source)
        if u'验证码' in super_man_driver.page_source:
            img = super_man_driver.find_element_by_id('J_code')
            button = super_man_driver.find_element_by_id('J_submit')
            input = super_man_driver.find_element_by_id('J_input')
            img_url = img.get_attribute('src')
            name = int(time.time())
            # ir = requests.get(img_url)
            # open('code/%s.jpg' % name, 'wb').write(ir.content)
            rc = RuoKuai(Config.ruokuai_name, Config.ruokuai_pswd, Config.ruokuai_soft_id, Config.ruokuai_soft_key)
            # im = open('code/%s.jpg' % name, 'rb').read()
            im = open(self.file_path + '/code/v4.jpg', 'rb').read()
            code = rc.rk_create(im, '2040')
            print(code)
            code_text = code['Result']
            print(code_text)
            input.send_keys(code_text)
            from selenium.webdriver import ActionChains

            actions = ActionChains(super_man_driver)
            actions.move_to_element(button)
            actions.click(button)
            actions.perform()
            # button.click()
            # driver.implicitly_wait(10)
        super_man_driver.quit()
        time.sleep(1)
