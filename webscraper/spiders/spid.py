from scrapy import Request
from scrapy.spiders import CrawlSpider
import pandas as pd
#from tqdm import tqdm
import re
import json
import os

class GsmArenaSpider(CrawlSpider):
    name = "gsmarena"
    allowed_domains = ['www.gsmarena.com']
    start_urls = ["https://www.gsmarena.com/makers.php3"]
    
    #schema = pd.MultiIndex.from_tuples(, names=[])
    data_dict = {"Brand": [], "Model": [], "Specifications": []}
    all_brands = {}
    page = 0
    
    visited_model_urls = open("visited_models.txt").read().split("\n")
    
    mylog = ""

    def parse(self, response):
        # All brands page parser
        self.page += 1
        with open("html_dump/all_brands.html", "w") as fw:
            fw.write(response.text)
        container = response.css("div.st-text")
        try:
            self.mylog += ("URL: %s\nTotal Page: %d\n" % (response.url, self.page))
            assert container
        except AssertionError:
            print("Not found Main container in Brands Page")
            self.mylog += ("ContainerError Brands Page: %s : Main container not found\n" % response.url)
            return
        brands = container.css("table tr > td > a")
        brands_dict = {"Brands": brands.xpath("./text()").getall(), 
                       "href": brands.xpath("./@href").getall(), 
                       "no_models": brands.xpath("./span/text()").getall()}
        no_brands = len(brands_dict["Brands"])
        try:
            assert no_brands + len(brands_dict["no_models"]) - len(brands_dict["href"]) == no_brands
        except AssertionError:
            self.mylog += "LengthError Brands Page: %s : (%d, %d, %d)" % (no_brands, len(brands_dict["no_models"]), len(brands_dict["href"]))
            return
        self.all_brands = brands_dict
        for i in range(no_brands):
            yield Request(response.urljoin(brands_dict["href"][i]), self.parse_models, meta={'brand': brands_dict["Brands"][i], 'brand_page': 1})

    def parse_models(self, response):
        # All models Page parser
        self.page += 1
        brand = response.meta.get('brand')
        brand_page = int(response.meta.get('brand_page'))
        #with open("html_dump/%s_%s.html" % (brand, self.page), "w") as fw:
            #fw.write(response.text)
        container = response.css("div.makers")
        try:
            self.mylog += ("Brand: %s : URL: %s\nBrand Page: %d\nTotal Page: %d\n" % (brand, response.url, brand_page, self.page))
            assert container
        except AssertionError:
            print("Not found Main container in Models Page")
            self.mylog += ("ContainerError All Models Page: %s : Main container not found\n" % response.url)
            return
        if self.page % 10 == 0:
            print("Page %d" % self.page)
        models_dict = {"Models": container.css("ul > li > a > strong > span::text").getall(),
                       "href": container.css("ul > li > a::attr(href)").getall()}
        no_models = len(models_dict["Models"])
        try:
            assert no_models == len(models_dict["href"])
        except AssertionError:
            self.mylog += "LengthError All Models Page: %s : (%d, %d)\n" % (response.url, no_models, len(models_dict["href"]))
            return
        # Extract specifications from the model page
        for i in range(no_models):
            next_url = response.urljoin(models_dict["href"][i])
            if next_url not in self.visited_model_urls:
                yield Request(next_url, self.parse_model, 
                              meta={'brand': brand, 'model': models_dict["Models"][i]})
        # Go to next page while exist
        nextPage = response.xpath("//a[@title='Next page']")
        if nextPage:
            classes = nextPage.attrib.get('class').split(" ")
            assert "pages-next" in classes, "Wrong nextPage element"
            if "disabled" not in classes:
                yield Request(response.urljoin(nextPage.attrib.get('href')), self.parse_models, 
                          meta={'brand': brand, 'brand_page': brand_page+1})
        else:
            print("Next Page not found")
            self.mylog += "Next Page not found\n"
    
    def parse_model(self, response):
        # Model Page parser
        self.page += 1
        model = response.meta.get('model')
        #with open("html_dump/%s_%s.html" % (model, self.page), "w") as fw:
            #fw.write(response.text)
        container = response.css("#specs-list")
        try:
            self.mylog += ("\nModel: %s\nTotal Page: %d\n" % (model, self.page))
            assert container
        except AssertionError:
            print("Not found Main container in Model Page")
            self.mylog += ("ContainerError Model Page: %s : Main container not found\n" % response.url)
            return
        feature_tables = container.xpath(".//table")
        specs = []
        for tbody in feature_tables:
            specs.append({
                tbody.css('tr:not([class*="tr-toggle"]) > th::text').get(): 
                dict([(f, v) 
                      for (f, v) in zip(tbody.css('tr:not([class*="tr-toggle"]) > td.ttl > a::text').getall(),
                                        tbody.css('tr:not([class*="tr-toggle"]) > td.nfo').xpath(".//text()").getall())])})
        try:
            assert specs
            assert specs[0]
        except AssertionError:
            self.mylog += "LengthError Model Page: %s : Specs - %s\n" % (response.url, specs)
            return

        self.data_dict["Specifications"].append(specs)
        self.data_dict["Brand"].append(response.meta.get('brand'))
        self.data_dict["Model"].append(model)
        self.visited_model_urls.append(response.url)
        #self.data_dict["URL"].append(response.url)
    
    def close(self, spider):
        print("%d pages" % self.page)
        with open("mylog.log", "w") as f:
            f.write(self.mylog)
        if self.page > 2:
            with open("visited_models.txt", "w") as fw:
                fw.write("\n".join(self.visited_model_urls))
                
            if os.path.isfile("gsmarena_data.csv"):
            	pd.DataFrame(self.data_dict).to_csv("gsmarena_data.csv", mode='a', index=False, header=False)
            else:
            	pd.DataFrame(self.data_dict).to_csv("gsmarena_data.csv", index=False)
            #pd.DataFrame(self.all_brands).to_csv("gsmarena_brands.csv", index=False)
            #if os.path.isfile("gsmarena_data.json"):
                #with open("gsmarena_data.json", "r") as f:
                    #data = json.load(f)
                #data["Brand"].extend(self.data_dict["Brand"])
                #data["Model"].extend(self.data_dict["Model"])
                #data["Specifications"].extend(self.data_dict["Specifications"])
                #data["URL"].extend(self.data_dict["URL"])
                #with open("gsmarena_data.json", "w") as fw:
                        #json.dump(data, fw)
            #else:
            	#json.dump(self.data_dict, open("gsmarena_data.json", "w"))


class AmazonSpider(CrawlSpider):
    name = "amazon"
    allowed_domains = ['amazon.in']
    start_urls = ["https://www.amazon.in/Smartphones-Basic-Mobiles/s?rh=n%3A1805560031&page=136"]#"https://www.amazon.in/Smartphones/b?ie=UTF8&node=1805560031"]
    
    df = pd.DataFrame(columns=["Model", "Price"])
    page = 0
    
    mylog = ""

    def parse(self, response):
        container = response.css("#mainResults")
        if not(container):
            self.parse_other(response)
            return
        self.page = 1
        self.mylog += ("Page %d\n\n" % self.page)
        phones_list = container.css("ul > li.s-result-item")
        models = phones_list.css("a > h2::text").getall()
        prices = phones_list.xpath(".//a//span[@class='currencyINR']/../text()").getall()
        if not(models):
            self.mylog += "Empty List\n"
        else:
            if len(models) != len(prices):
                self.mylog += "Length mismatch\n"
                assert len(models) == len(phones_list), "Not all models have been extracted"
                assert len(prices) < len(models), "Prices is longer"
                models = []
                prices = []
                for phone in phones_list:
                    models.append(phone.css("a > h2::text").get())
                    price = phone.xpath(".//a//span[@class='currencyINR']/../text()").get()
                    if price:
                        prices.append(price)
                    elif re.match(".*(unavailable).*", phone.css('div.a-row.a-spacing-none::text').get(), re.DOTALL):
                        prices.append('-1')
                    else:
                        prices.append('-2')
            self.df = self.df.append(pd.DataFrame({"Model": models, "Price": prices}), ignore_index=True)
        # Go to next page while exist
        nextPage = response.xpath("//a[@id='pagnNextLink']/@href").get()
        if nextPage:
            yield Request(response.urljoin(nextPage), self.parse_other)
        else:
            print("2nd Page Not found")
            
    def parse_other(self, response):
        self.page += 1
        if self.page % 10 == 0:
            print("Page %d" % self.page)
        self.mylog += ("\n\nPage %d\n\n" % self.page)
        container = response.css("span div.s-result-list.s-search-results")
        if not(container):
            raise NotFoundError
        phones_list = container.css("div.a-section.a-spacing-medium")
        models = phones_list.css("h2 > a > span::text").getall()
        prices = phones_list.xpath(".//a//span[@data-a-color='price']//span[@class='a-price-whole']/text()").getall()
        if not(models):
            self.mylog += "Empty List\n"
        else:
            if len(models) != len(prices):
                self.mylog += "Length mismatch\n"
                assert len(models) == len(phones_list), "Not all models have been extracted"
                assert len(prices) < len(models), "Prices is longer"
                models = []
                prices = []
                for phone in phones_list:
                    models.append(phone.css("h2 > a > span::text").get())
                    price = phone.xpath(".//a//span[@data-a-color='price']//span[@class='a-price-whole']/text()").get()
                    if price:
                        prices.append(price)
                    elif re.match(".*(unavailable).*", phone.get(), re.DOTALL):
                        prices.append('-1')
                    else:
                        prices.append('-2')
            self.df = self.df.append(pd.DataFrame({"Model": models, "Price": prices}), ignore_index=True)
        # Go to next page while exist
        nextPage = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a/@href").get()
        if nextPage:
            yield Request(response.urljoin(nextPage), self.parse_other)
        else:
            print("End Reached")

    def close(self, spider):
        print("%d pages" % self.page)
        if self.page > 1:
            with open("mylog.log", "w") as f:
                f.write(self.mylog)
            self.df.to_csv("data.csv", index=False)
