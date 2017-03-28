# -*- coding:utf-8 -*-

import scrapy
import codecs
import time
import re
from tianyancha.items import TianyanchaItem
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class TianYanCha_Spider(CrawlSpider):
    name = 'tyc_spider'
    start_urls = ['http://www.tianyancha.com                 ']

    def parse(self, response):
        with codecs.open('../company_test.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                url = str(line.replace('\r', '').replace('\n', '').replace('=', ''))
                requests = scrapy.Request(url, callback=self.parse_page)
                yield requests

    def parse_page(self, response):
        # try:
        print response.body
        item = TianyanchaItem()
        l = ItemLoader(item=item, response=response)
        company_id = response.url[34:]
        company_name = response.selector.xpath('//div[@class="company_info_text"]/div[1]/text() | //span[@class="base-company f16 ng-binding"]/text()').extract()[0]
        legal_representative = response.selector.xpath(u'//div[text()="法定代表人"]/following-sibling::div[1]/a/text() | //a[@ng-if="company.baseInfo.legalPersonName"]/text()').extract()[0]
        registered_capital = response.selector.xpath(u'//div[text()="注册资本"]/following-sibling::div[1]/text() | //td[@class="td-regCapital-value"]/p/text()').extract()[0]
        registered_time = response.selector.xpath(u'//div[text()="注册时间"]/following-sibling::div[1]/text() | //td[@class="td-regTime-value"]/p/text()').extract()[0]
        condition = response.selector.xpath(u'//div[text()="状态"]/following-sibling::div[1]/text() | //td[@class="td-regStatus-value"]/p/text()').extract()[0]
        temp_items = response.selector.xpath('//td[@class="basic-td"]/div[1]/span/text()').extract()
        if temp_items:
            registered_number = temp_items[0]
            organization_number = temp_items[1]
            credit_number = temp_items[2]
            enterprise_type = temp_items[3]
            industry = temp_items[4]
            operating_period = temp_items[5]
            approved_date = temp_items[6]
            registration_authority = temp_items[7]
        else:
            registered_number = response.selector.xpath('//p[@ng-if="company.baseInfo.regNumber"]/text()').extract_first(default=u'未公开')
            organization_number = response.selector.xpath('//p[@ng-if="company.baseInfo.orgNumber"]/text()').extract_first(default=u'未公开')
            credit_number = response.selector.xpath('//p[@ng-if="company.baseInfo.creditCode"]/text()').extract_first(default=u'未公开')
            enterprise_type = response.selector.xpath('//p[@ng-if="company.baseInfo.companyOrgType"]/text()').extract_first(default=u'未公开')
            industry = response.selector.xpath('//p[@ng-if="company.baseInfo.industry"]/text()').extract_first(default=u'未公开')
            operating_period = response.selector.xpath('//p[@ng-if="company.baseInfo.fromTime"]/text()').extract_first(default=u'未公开')
            approved_date = response.selector.xpath('//p[@ng-if="company.baseInfo.estiblishTime"]/text()').extract_first(default=u'未公开')
            registration_authority = response.selector.xpath('//p[@ng-if="company.baseInfo.regInstitute"]/text()').extract_first(default=u'未公开')
        registered_address = response.selector.xpath('//td[@class="basic-td ng-scope"]/div/span/text() | //p[@ng-if="company.baseInfo.regLocation"]/text()').extract_first(default=u'暂无')
        business_scope = response.selector.xpath('//td[@class="basic-td ng-scope"]/div/span/span/text() | //span[@ng-if="company.baseInfo.businessScope"]/text()').extract_first(default=u'暂无')
        telephone = response.selector.xpath('//div[@class="company_info_text"]/span/text()').extract_first(default=u'暂无')
        try:
            email = response.selector.xpath('//div[@class="company_info_text"]/span/text()').extract[1]
        except:
            email = u'暂无'
        try:
            address = response.selector.xpath('//div[@class="company_info_text"]/span/text()').extract[5]
        except:
            address = u'暂无'
        #website.xpath //div[@class="company_info_text"]/span[3]/a/text() | //div[@class="company_info_text"]/span[3]/span[2]/text() |
        website = response.selector.xpath('//a[@ng-if="company.websiteList"]/text()').extract_first(default=u'暂无')
        score = response.selector.xpath('//td[@class="td-score position-rel"]/img/@ng-alt | //img[@class="td-score-img"]/@ng-alt').extract()[0][-2:]
        logo_location = response.selector.xpath('//div[@class="company_info"]/div[1]/img/@src').extract()[0]
        former_name = response.selector.xpath(u'//span[text()="曾用名"]/following-sibling::span[2]/text()').extract_first(default='None')

        # 有一些logo的链接坏掉了，网站给出了备用logo
        # logo_location = response.xpath('//div[@class="company_info"]/div[1]/img/@onerror').extract()[0].replace('this.src=', '').replace("'", '')
        # logo_location = http://static.tianyancha.com/wap/images/company_pic_v2.png
        # person_id = response.selector.xpath(
        #     '//div[@class="staffinfo-module-container ng-scope"]/div/div/div[2]/div[1]/a/@href').extract()
        # person_name = response.selector.xpath(
        #     '//div[@class="staffinfo-module-container ng-scope"]/div/div/div[2]/div[1]/a/text()').extract()
        # position = response.selector.xpath(
        #     '//div[@class="staffinfo-module-container ng-scope"]/div/div/div[2]/div[2]/span/text()').extract()
        # if person_id:
        #     for i in range(0, len(person_id)):
        #         person_id[i] = person_id[i][7:]
        # else:
        #     person_id = ['None']
        #     person_name = ['None']
        #     position = ['None']
        # if not position:
        #     position = ['None']

        # shareholder_id = response.selector.xpath(
        #     '//div[@ng-if="dataItemCount.holderCount>0"]/table/tbody/tr/td/a/@href').extract()
        # shareholder_name = response.selector.xpath(
        #     '//div[@ng-if="dataItemCount.holderCount>0"]/table/tbody/tr/td[1]/a/text()').extract()
        # investment_proportion = response.selector.xpath(
        #     '//div[@ng-if="dataItemCount.holderCount>0"]/table/tbody/tr/td[2]/div/div/span/text()').extract()
        # subscribed_contribution = response.selector.xpath(
        #     '//div[@ng-if="dataItemCount.holderCount>0"]/table/tbody/tr/td[3]/div/span[@class="ng-binding"]/text()').extract()
        # if shareholder_id:
        #     for i in range(0, len(shareholder_id)):
        #         shareholder_id[i] = shareholder_id[i][7:]
        #
        #     really_contribution = []
        #     for i in range(0, len(shareholder_name)):
        #         temp = response.selector.xpath(
        #             u'//span[text()="%s"]/parent::*/parent::td/following-sibling::td[1]/div/span/text()' %
        #             subscribed_contribution[i]).extract_first(default=u'暂无')
        #         really_contribution.append(str(temp))
        # else:
        #     shareholder_id = ['None']
        #     shareholder_name = ['None']
        #     investment_proportion = ['None']
        #     subscribed_contribution = ['None']
        #     really_contribution = ['None']

        l.add_value("company_name", company_name)
        l.add_value("legal_representative", legal_representative)
        l.add_value("registered_capital", registered_capital)
        l.add_value("registered_time", registered_time)
        l.add_value("condition", condition)
        l.add_value("registered_number", registered_number)
        l.add_value("organization_number", organization_number)
        l.add_value("credit_number", credit_number)
        l.add_value("enterprise_type", enterprise_type)
        l.add_value("industry", industry)
        l.add_value("operating_period", operating_period)
        l.add_value("approved_date", approved_date)
        l.add_value("registration_authority", registration_authority)
        l.add_value("registered_address", registered_address)
        l.add_value("business_scope", business_scope)
        l.add_value("telephone", telephone)
        l.add_value("email", email)
        l.add_value("website", website)
        l.add_value("logo_location", logo_location)
        l.add_value("address", address)
        l.add_value("score", score)
        l.add_value("company_id", company_id)
        l.add_value("former_name", former_name)

        # l.add_value("person_id", person_id)
        # l.add_value("person_name", person_name)
        # l.add_value("position", position)

        # l.add_value("shareholder_id", shareholder_id)
        # l.add_value("shareholder_name", shareholder_name)
        # l.add_value("investment_proportion", investment_proportion)
        # l.add_value("subscribed_contribution", subscribed_contribution)
        # l.add_value("really_contribution", really_contribution)

        print "ONE OK"
        yield l.load_item()
        # except Exception as e:
        #     pass
            # print e
            # print response.body



        # except Exception as e:
        #     print "ONE FAIL"
        #     with codecs.open('log.txt', 'a', encoding='utf-8') as f:
        #         time_now = time.asctime(time.localtime(time.time()))
        #         f.write(strresponse.url) + ' ' + str(e) + ' ' + str(time_now) + '\r')


