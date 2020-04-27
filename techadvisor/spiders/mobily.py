# -*- coding: utf-8 -*-
import scrapy
import re
import unidecode
from bs4 import BeautifulSoup

from  techadvisor.items import TechadvisorItem


class Techadvisor(scrapy.Spider):
    name = 'techadvisor'
    allowed_domains = ['techadvisor.co.uk']
    start_urls = ['https://www.techadvisor.co.uk/review/smartphones/']

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse_product_details(self, response):
        try:
            item = TechadvisorItem()
            specs = response.xpath('//div[@id="showProductSpecificationFull"]//li//text()').extract()

            if(specs):

                regex_battery = r'(\d+(.|,)?\d*)(m|M)(a|A)(h|H)'
                regex_weight = r'([0-9]+)(\s*)g'
                regex_resolution = r'([0-9 ]+x[0-9 ]+)'
                regex_dimensions = r'((\d+\.?\d*)(x| x )(\d+\.?\d*)(x| x )(\d+\.?\d*))(mm| mm)'
                
                try:
                    r_battery = re.compile(regex_battery)
                    r_weight = re.compile(regex_weight)
                    r_resolution = re.compile(regex_resolution)
                    r_dimensions = re.compile(regex_dimensions)
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print("Not able to compile regex")

                try:
                    battery = list(filter(r_battery.search, specs))
                    if(len(battery) > 0):
                        item['battery_capacity'] = re.search(regex_battery, battery[0]).group(1).replace(' ', '').replace(',', '').replace('.', '')
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch battery')

                try:
                    weights = list(filter(r_weight.search, specs))
                    weightsReplaced = [i.replace(' ', '') for i in weights] 
                    regex_weight_exactly = r'^([0-9]+)(\s*)g\Z$'
                    r_weight_exactly = re.compile(regex_weight_exactly)
                    weight = list(filter(r_weight_exactly.search, weightsReplaced))
                    if(weight):
                        item['weight'] = weight[0].replace('g', '')
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch weight')

                try:
                    resolutions = list(filter(r_resolution.search, specs))

                    if(len(resolutions) > 0):
                        for resolution in resolutions:
                            if not 'mm' in resolution:

                                x = re.search(r_resolution, resolution).group(1).replace(' ', '')
                                res = x.split('x')
                                
                                if(len(res[0])>4):
                                    res[0] = ''
                                    res[0] = res[0][1:]
                                if(len(res[1])>3):
                                    res[1] = ''
                                    res[1] = res[1][0:4]

                                
                                if(res[0] != "" and res[1] != ""):
                                    if(int(res[0]) < int(res[1])):
                                        item['screen_resolution'] = res[1] + 'x' + res[0]  
                                    else:
                                        item['screen_resolution'] = res[0] + 'x' + res[1]
                                    break

                        try:
                            if(len(item['screen_resolution']) < 6):
                                item['screen_resolution'] = ''
                        except:
                            pass
                            
            
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch screen resolution')


                try:
                    dimension = list(filter(r_dimensions.search, specs))
                    if(len(dimension) > 0):
                        dimensionString = re.search(r_dimensions, dimension[0]).group(1).replace(' ', '').split('x')

                        dims = []
                        for dim in dimensionString:
                            dims.append(float(dim))

                        dims.sort(reverse=True)

                        dimsText = []
                        for dim in dims:
                            dimsText.append(str(dim))

                        item['dimensions'] = dimsText
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch dimensions')

                try:
                    item['url_web'] = response.url.split("?p=", 1)[0]
                    item['date_published'] = response.xpath('//span[@class="publicationDate"]//time//@datetime').extract()[0]
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch url_web or date published')

                try:
                    headers = response.xpath('//h3//text()').extract()
                    for header in headers:
                        if 'Specs' in header:
                            item['name'] = header.replace(': Specs', '')
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch name')
                
                # item['text'] = self.text
                # self.text = ''

                yield item

            else:
                try:
                    name = ''
                    name = response.xpath('//meta[@itemprop="name"]//@content').extract()[0]
                    item['url_web'] = response.url.split("?p=", 1)[0]
                    item['name'] = name.strip()
                    
                    if(len(name) > 0):
                        yield item
                except Exception as e: 
                    print(e)
                    print(response.url)
                    print('Not able to fetch only name and url')

        except Exception as e: 
            print(e)
                
    # text = ''

    # def parse_text(self, response):
    #     try:
    #         soup = BeautifulSoup(response.text, features="lxml")
    #         t =  [p.get_text().strip() for p in soup.find_all('p')]
    #         new = ''.join(t)
    #         self.text += new

    #     except Exception as e: 
    #         print(e)
    #         print(response.url)
    #         print('Not able to fetch text')

    lastPageNumber = 1

    def parse_product(self, response):
        try:
            lastPageFound = response.xpath("//ul[@class='pagination']//li//@href").extract()

            regex_last_page_number = r'(p=\d+)'
            regex_number = r'(\d+)'
            
            if(len(lastPageFound) > 0):
                for page in lastPageFound:
                    pNum = re.findall(regex_last_page_number, page)[0]
                    if(len(pNum) > 0):
                        num = int(re.findall(regex_number, str(pNum))[0])
                        if(num != None):
                            if num > self.lastPageNumber:
                                self.lastPageNumber = num

            url = response.url.split("?p=", 1)[0]
            url = url + '?p=' + str(self.lastPageNumber)
            
            # getTextNum = self.lastPageNumber + 1
            # for i in range(1, getTextNum):
            #     urlText = response.url.split("?p=", 1)[0]
            #     urlText = urlText + '?p=' + str(i)
            #     yield scrapy.Request(url=urlText, callback=self.parse_text)

            self.lastPageNumber = 1

            yield scrapy.Request(url=url, callback=self.parse_product_details)
            
        except Exception as e: 
            print(e)


    def parse_products(self, response):
        try:
            
            links_to_products = response.xpath('//a[@class="thumb"]/@href').extract()
            for link in links_to_products:
                if('https://www.techadvisor.co.uk/review/smartphones/' in link and not 'comparison' in link and not 'vs' in link):
                        yield scrapy.Request(url=link, callback=self.parse_product)

        except Exception as e:
            print(e)
  
    def parse(self, response):
        try:

            lastLink = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "listingPagination", " " ))]//li//@href').extract()[-2]
            regex_number = r'(\d+)'
            lastNumber = int(re.findall(regex_number, lastLink)[0])
            defaultLink = 'https://www.techadvisor.co.uk/review/smartphones/?p='

            for x in range(lastNumber):
                link = defaultLink + str(x)
                yield scrapy.Request(url=link, callback=self.parse_products)

        except Exception as e:
            print(e)
        