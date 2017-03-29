# -*- coding:utf-8 -*-

import scrapy
import codecs
import time
import re
import json
from tianyancha.items import TianyanchaItem
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class TianYanCha_Spider(CrawlSpider):
    name = 'tyc_spider'
    start_urls = ['http://www.tianyancha.com                 ']

    def parse(self, response):
        with codecs.open('../company_test.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                url = str(line.replace('\r', '').replace('\n', '').replace('=', ''))
                requests = scrapy.Request(url, callback=self.parse_basicinfo)
                yield requests

    def parse_basicinfo(self, response):
        item = TianyanchaItem()
        company_id = response.url[34:]
        company_name = response.selector.xpath('//div[@class="company_info_text"]/div[1]/text()').extract()[0]
        legal_representative = response.selector.xpath(u'//div[text()="法定代表人"]/following-sibling::div[1]/a/text()').extract_first(default=u'未公开')
        registered_capital = response.selector.xpath(u'//div[text()="注册资本"]/following-sibling::div[1]/text()').extract_first(default=u'未公开')
        registered_time = response.selector.xpath(u'//div[text()="注册时间"]/following-sibling::div[1]/text()').extract_first(default=u'未公开')
        condition = response.selector.xpath(u'//div[text()="状态"]/following-sibling::div[1]/text()').extract_first(default=u'未公开')
        temp_items = response.selector.xpath('//td[@class="basic-td"]/div[1]/span/text()').extract()
        registered_number = temp_items[0]
        organization_number = temp_items[1]
        credit_number = temp_items[2]
        enterprise_type = temp_items[3]
        industry = temp_items[4]
        operating_period = temp_items[5]
        approved_date = temp_items[6]
        registration_authority = temp_items[7]
        registered_address = response.selector.xpath('//td[@class="basic-td ng-scope"]/div/span/text()').extract_first(default=u'暂无')
        business_scope = response.selector.xpath('//td[@class="basic-td ng-scope"]/div/span/span/text()').extract_first(default=u'暂无')
        telephone = response.selector.xpath('//div[@class="company_info_text"]/span[1]/text()').extract_first(default=u'暂无')
        email = response.selector.xpath('//div[@class="company_info_text"]/span[2]/text()').extract_first(default=u'暂无')
        address = response.selector.xpath('//div[@class="company_info_text"]/span[4]/text()').extract_first(default=u'暂无')
        website = response.selector.xpath('//div[@class="company_info_text"]/span[3]/a/text()').extract_first(default=u'暂无')
        score = response.selector.xpath('//td[@class="td-score position-rel"]/img/@ng-alt | //img[@class="td-score-img"]/@ng-alt').extract()[0][-2:]
        logo_location = response.selector.xpath('//div[@class="company_info"]/div[1]/img/@src').extract()[0]
        former_name = response.selector.xpath(u'//span[text()="曾用名"]/following-sibling::span[2]/text()').extract_first(default=u'无')

        flag = response.selector.xpath('//div[@class="company_container"]/div/div/div/@class').extract()
        for i in range(0, len(flag)):
            if flag[i][-7:] == u'disable':
                flag[i] = 0
            else:
                flag[i] = 1

        item["flag"] = flag
        item["company_name"] = company_name
        item["legal_representative"] = legal_representative
        item["registered_capital"] = registered_capital
        item["registered_time"] = registered_time
        item["condition"] = condition
        item["registered_number"] = registered_number
        item["organization_number"] = organization_number
        item["credit_number"] = credit_number
        item["enterprise_type"] = enterprise_type
        item["industry"] = industry
        item["operating_period"] = operating_period
        item["approved_date"] = approved_date
        item["registration_authority"] = registration_authority
        item["registered_address"] = registered_address
        item["business_scope"] = business_scope
        item["telephone"] = telephone
        item["email"] = email
        item["website"] = website
        item["logo_location"] = logo_location
        item["address"] = address
        item["score"] = score
        item["company_id"] = company_id
        item["former_name"] = former_name

        next_url = "http://www.tianyancha.com/expanse/staff.json?id=" + str(item["company_id"]) + "&ps=20&pn=1"
        request = scrapy.Request(url=next_url, meta={"item": item, "flag": flag}, callback=self.parse_mainperson)
        yield request

    def parse_mainperson(self, response):
        flag = response.meta["flag"]
        item = response.meta["item"]
        if flag[2] == 1:
            data = json.loads(response.body)

            person_id = []
            person_name = []
            position = []

            n = data["data"]["total"]
            for i in range(0, n):
                person_id.append(data["data"]["result"][i]["id"])
                person_name.append(data["data"]["result"][i]["name"])
                position.append(data["data"]["result"][i]["typeJoin"][0])

            item["person_id"] = person_id
            item["person_name"] = person_name
            item["position"] = position

        next_url = "http://www.tianyancha.com/expanse/holder.json?id=" + str(item["company_id"]) + "&ps=20&pn=1"
        request = scrapy.Request(url=next_url, meta={"item": item, "flag": flag}, callback=self.parse_hareholderinfo)
        yield request

    def parse_hareholderinfo(self, response):
        flag = response.meta["flag"]
        item = response.meta["item"]
        if flag[3] == 1:
            data = json.loads(response.body)

            shareholder_id = []
            shareholder_name = []
            investment_proportion = []
            subscribed_contribution = []
            subscribed_contribution_time = []
            really_contribution = []

            n = data["data"]["total"]
            for i in range(0, n):
                shareholder_id.append(data["data"]["result"][i]["id"])
                shareholder_name.append(data["data"]["result"][i]["name"])
                investment_proportion.append(data["data"]["result"][i]["capital"][0]["percent"])
                subscribed_contribution.append(data["data"]["result"][i]["capital"][0]["amomon"])

                try:
                    subscribed_contribution_time.append(data["data"]["result"][i]["capital"][0]["time"] or u'无')
                except:
                    subscribed_contribution_time.append(u'无')

                try:
                    really_contribution.append(data["data"]["result"][i]["capitalActl"][0]["amomon"] or u'无')
                except:
                    really_contribution.append(u'无')

            item["shareholder_id"] = shareholder_id
            item["shareholder_name"] = shareholder_name
            item["investment_proportion"] = investment_proportion
            item["subscribed_contribution"] = subscribed_contribution
            item["subscribed_contribution_time"] = subscribed_contribution_time
            item["really_contribution"] = really_contribution

        item["invested_company_id"] = []
        item["invested_company_name"] = []
        item["invested_representative"] = []
        item["registered_cap"] = []
        item["investment_amount"] = []
        item["investment_prop"] = []
        item["registered_date"] = []
        item["condit"] = []

        next_url = "http://www.tianyancha.com/expanse/inverst.json?id=" + str(item["company_id"]) + "&ps=20&pn=1"
        request = scrapy.Request(url=next_url, meta={"item": item, "flag": flag}, callback=self.parse_investment)
        yield request

    def parse_investment(self, response):
        flag = response.meta["flag"]
        item = response.meta["item"]

        invested_company_id = item["invested_company_id"]
        invested_company_name = item["invested_company_name"]
        invested_representative = item["invested_representative"]
        registered_cap = item["registered_cap"]
        investment_amount = item["investment_amount"]
        investment_prop = item["investment_prop"]
        registered_date = item["registered_date"]
        condit = item["condit"]

        if flag[4] == 1:
            data = json.loads(response.body)
            for dic in data["data"]["result"]:
                invested_company_id.append(dic["id"])
                invested_company_name.append(dic["name"])
                invested_representative.append(dic["legalPersonName"])
                try:
                    registered_cap.append(dic["regCapital"] or u'无')
                except:
                    registered_cap.append(u'无')
                if dic["amount"] == 0:
                    investment_amount.append(u'无')
                else:
                    try:
                        investment_amount.append(str(dic["amount"]) + u'万元人民币')
                    except:
                        investment_amount.append(u'无')
                try:
                    investment_prop.append(dic["percent"] or u'无')
                except:
                    investment_prop.append(u'无')
                date = time.strftime("%Y-%m-%d", time.localtime(int(str(dic["estiblishTime"])[:10])))
                registered_date.append(str(date))
                condit.append(dic["regStatus"])

            item["invested_company_id"] = invested_company_id
            item["invested_company_name"] = invested_company_name
            item["invested_representative"] = invested_representative
            item["registered_cap"] = registered_cap
            item["investment_amount"] = investment_amount
            item["investment_prop"] = investment_prop
            item["registered_date"] = registered_date
            item["condit"] = condit

        if len(response.body) > 3000:
            next_url = str(response.url)[:-1] + str(int(str(response.url)[-1]) + 1)
            request = scrapy.Request(url=next_url, meta={"item": item, "flag": flag}, callback=self.parse_investment)
            yield request

        item["change_time"] = []
        item["change_item"] = []
        item["before_change"] = []
        item["after_change"] = []

        next_url = 'http://www.tianyancha.com/expanse/changeinfo.json?id=' + str(item["company_id"]) + '&ps=5&pn=1'
        request = scrapy.Request(url=next_url, meta={"item": item, "flag": flag}, callback=self.parse_changerecord)
        yield request

    def parse_changerecord(self, response):
        flag = response.meta["flag"]
        item = response.meta["item"]

        change_time = item["change_time"]
        change_item = item["change_item"]
        before_change = item["before_change"]
        after_change = item["after_change"]

        if flag[5] == 1:
            data = json.loads(response.body)
        print data
        return item



