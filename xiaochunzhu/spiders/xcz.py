# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
import json
import browsercookie
import pandas as pd
from pandas import Series,DataFrame
import os

class XczSpider(scrapy.Spider):
    name = 'xcz'
    # allowed_domains = ['www.incnjp.com']
    start_urls = ['https://www.incnjp.com/api/v8/threads?fid=15&filter=author&order&page=']
    message_urls = ['https://www.incnjp.com/api/v8/thread?tid=']

    title_headers = {
        'path':'/api/v8/threads?fid=15&page='
    }
    cookie_k = []
    cookie_v = []
    for cookie in browsercookie.chrome():
        if ('www.incnjp.com'.rfind(str(cookie.domain)) != -1):
            # print("cookie:" + str(cookie.domain))
            # print("cookie:" + str(cookie.name))
            cookie_k.append(cookie.name)
            cookie_v.append(cookie.value)
    cookies = dict(zip(cookie_k, cookie_v))
    print(cookies)

    page_index = range(1,635)
    page = 1

    def start_requests(self):
        # print("开始")
        for i in self.page_index :
            self.title_headers = {
                'path':'/api/v8/threads?fid=15&page='+str(i)
            }
            yield Request(url=self.start_urls[0]+str(i),headers=self.title_headers,cookies=self.cookies ,callback=self.parse)

    def parse(self, response):
        shuju = json.loads(response.text)
        # print("来了")
        df_index = 0
        for title in shuju['Content']['threadlist'] :
            # print(title)
            df = pd.DataFrame(title,index=[df_index])
            # print(df)
            # if df_index >0 :
            #     df.to_csv(path_or_buf='/Users/Phantom/Desktop/xiaochun.csv',mode='a',header=False)
            # else:df.to_csv(path_or_buf='/Users/Phantom/Desktop/xiaochun.csv')
            # 相亲具体要求
            message_headers = {
                'path': '/api/v8/thread?tid='+shuju['Content']['threadlist'][df_index]['tid']
            }
            # print('path is ' + message_headers['path'])
            message_url = self.message_urls[0] + shuju['Content']['threadlist'][df_index]['tid']
            yield Request(url=message_url, headers=message_headers, callback=self.message_parse, meta={'list':df,'number':df_index})
            df_index = df_index + 1

    def message_parse(self, response):
        content_index = response.meta['number']

        content = json.loads(response.text)
        authorid = content['Content']['thread']['authorid']
        postlist = content['Content']['postlist']
        json_postlist = json.dumps(postlist)
        message =content['Content']['thread']['message']
        data = {'authorid':authorid,'message':message,'postlist':json_postlist}
        content_data= DataFrame(data,index=[content_index])
        # 列表
        list_data = response.meta['list']
        # 内容
        all_data = pd.merge(list_data,content_data)

        all_data.index = [self.page]
        # 写入csv文件
        if os.path.isfile('/Users/Phantom/Desktop/xiaochun.csv') :
            all_data.to_csv(path_or_buf='/Users/Phantom/Desktop/xiaochun.csv',mode='a', header=False)
        else:
            all_data.to_csv(path_or_buf='/Users/Phantom/Desktop/xiaochun.csv', header=True)

        self.page = self.page + 1


