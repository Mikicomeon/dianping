# -*- coding: utf-8 -*-

from random import choice

class Proxies:
    @staticmethod
    def get_proxies():
        proxies = [
            #{"http": "http://111.206.81.248:80", "https": "https://111.206.81.248:80"},
            #{"http": "http://47.88.12.208:8088", "https": "https://47.88.12.208:8088"},
            #{"http": "http://47.88.22.173:8088", "https": "https://47.88.22.173:8088"}
        ]
        return choice(proxies)
