# -*- coding: utf-8 -*-
import scrapy
import re
import unidecode

from  techadvisor.items import TechadvisorItem


class Techadvisor(scrapy.Spider):
    name = 'techadvisor'
    allowed_domains = ['techadvisor.co.uk']
    start_urls = ['https://www.techadvisor.co.uk/review/smartphones/']

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    lastPage = False
    def parse_products_details(self, response):
        item = TechadvisorItem()
        lastPageFound = response.xpath("//ul[@class='pagination']//li//@href").extract()

        if(lastPageFound and (not self.lastPage)):
            self.lastPage = True
            lastPageFound = response.xpath("//ul[@class='pagination']//li//@href").extract()[-1]
            yield scrapy.Request(url=lastPageFound, callback=self.parse_products_details)


        specs = response.xpath('//div[@id="showProductSpecificationFull"]//li//text()').extract()

        if(specs):

            regex_battery = '(\d+(.|,)?\d*)(m|M)(a|A)(h|H)'
            regex_weight = '([0-9]+)(\s*)g'
            regex_resolution = '([0-9 ]+x[0-9 ]+)'
            regex_dimensions = '((\d+\.?\d*)(x| x )(\d+\.?\d*)(x| x )(\d+\.?\d*))(mm| mm)'

            r_battery = re.compile(regex_battery)
            r_weight = re.compile(regex_weight)
            r_resolution = re.compile(regex_resolution)
            r_dimensions = re.compile(regex_dimensions)

            battery = list(filter(r_battery.search, specs))[0]
            item['battery_capacity'] = re.search(regex_battery, battery).group(1).replace(' ', '').replace(',', '').replace('.', '')

            weights = list(filter(r_weight.search, specs))
            weightsReplaced = [i.replace(' ', '') for i in weights] 
            regex_weight_exactly = '^([0-9]+)(\s*)g\Z$'
            r_weight_exactly = re.compile(regex_weight_exactly)
            weight = list(filter(r_weight_exactly.search, weightsReplaced))
            if(weight):
                item['weight'] = weight[0].replace('g', '')

            resolutions = list(filter(r_resolution.search, specs))
            for resolution in resolutions:
                if not 'mm' in resolution:
                    item['screen_resolution'] = re.search(r_resolution, resolution).group(1).replace(' ', '')
                    res = item['screen_resolution'].split('x')
                    if(len(res[0])>4):
                        res[0] = res[0][1:]
                    if(len(res[1])>3):
                        res[1] = res[1][0:4]
                    
                    if(int(res[0]) < int(res[1])):
                        item['screen_resolution'] = res[1] + 'x' + res[0]  
                    else:
                        item['screen_resolution'] = res[0] + 'x' + res[1]
                    break

            if(len(item['screen_resolution']) < 6):
                item['screen_resolution'] = ''

            dimension = list(filter(r_dimensions.search, specs))[0]

            dimensionString = re.search(r_dimensions, dimension).group(1).replace(' ', '').split('x')

            dims = []
            for dim in dimensionString:
                dims.append(float(dim))

            dims.sort(reverse=True)

            dimsText = []
            for dim in dims:
                dimsText.append(str(dim))

            item['dimensions'] = dimsText


            item['url_web'] = response.url.replace('?p=2', '')

            headers = response.xpath('//h3//text()').extract()
            for header in headers:
                if 'Specs' in header:
                    item['name'] = header.replace(': Specs', '')
            
            self.lastPage = False

            yield item

    def parse_products(self, response):
        try:
            
            links_to_products = response.xpath('//a[@class="thumb"]/@href').extract()
            for link in links_to_products:
                if('https://www.techadvisor.co.uk/review/smartphones/' in link and not 'comparison' in link and not 'vs' in link):
                    yield scrapy.Request(url=link, callback=self.parse_products_details)

        except Exception as e:
            print(e)
  
    def parse(self, response):
        try:

            lastLink = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "listingPagination", " " ))]//li//@href').extract()[-2]
            regex_number = '(\d+)'
            lastNumber = int(re.findall(regex_number, lastLink)[0])
            defaultLink = 'https://www.techadvisor.co.uk/review/smartphones/?p='

            for x in range(lastNumber):
                link = defaultLink + str(x)
                yield scrapy.Request(url=link, callback=self.parse_products)

        except Exception as e:
            print(e)
        





        

        








