import requests
from bs4 import BeautifulSoup as BS
import os
import re
import random
import sys




class WebGraber():
    def __init__(self, start_url, crawling_rules, max_depth):
        self.start_url=start_url
        self.crawling_rules=crawling_rules
        self.max_depth=max_depth
        self.main_urls=[]
        self.sub_urls=set([])

        if self.max_depth>2:
            print("Maximum 2 levels are allowed")
            sys.exit()
        self.BASE_DIR=os.getcwd()
        self.BASE_DIR_CRAWLER=os.path.join(self.BASE_DIR,"crawler")
        if os.path.exists(self.BASE_DIR):
            self.BASE_DIR_CRAWLER=os.path.join(self.BASE_DIR,"crawler-{}".format(str(random.randint(1,40))))
            os.mkdir(self.BASE_DIR_CRAWLER)
        else:
            os.mkdir(self.BASE_DIR_CRAWLER)
        #extracting content from main page #level-0
        for rule in self.crawling_rules:
            if rule[0].search(self.start_url):
                self.base_url=self.start_url
                bs_response=self.download_url(self.start_url)
                self.save_to_disk(self.start_url,bs_response)
                self.main_urls=self.parse_page(bs_response,rule[1])
                self.main_urls=self.filter_allowed_urls(self.main_urls)

        if self.max_depth in range(0,3):
            for url in self.main_urls:
                self.sub_urls=set([])
                for rule in self.crawling_rules:
                    if rule[0].search(self.start_url+url):
                        print("visiting main category => ",url)
                        bs_response=self.download_url(self.start_url+url)
                        self.save_to_disk(url,bs_response)
                        sub_urls=self.parse_page(bs_response,rule[1])
                        if self.max_depth==2:
                            #level 2
                            for sub_url in sub_urls:
                                if not sub_url.startswith("."):
                                    if "/" in url:
                                        sub_url=url.rsplit("/",1)[0]+"/"+sub_url
                                    self.sub_urls.add(sub_url)

                            self.sub_urls=self.filter_allowed_urls(self.sub_urls)
                            if self.sub_urls:
                                for sub_url in self.sub_urls:
                                    print(" sub category => ",sub_url)
                                    bs_response=self.download_url(self.start_url+sub_url)
                                    self.save_to_disk(sub_url,bs_response)




    def download_url(self,url):
        response = requests.get(url)
        if response.status_code != 200:
            print("Error while extracting url. Please check your url and version number")
            sys.exit()
        return BS(response.text, 'html.parser')

    def parse_page(self,html,css):
        parse_urls=set([])
        if css:
            block=html.select_one(css)
            for url in block.find_all("a"):
                parse_urls.add(url.get('href'))
        else:
            for url in html.find_all("a"):
                parse_urls.add(url.get('href'))
        return parse_urls


    def save_to_disk(self,url,content):
        #if url is base_url then save it to root dir
        if self.crawling_rules[0][0].search(url):
            with open(os.path.join(self.BASE_DIR_CRAWLER,'home.txt'), "w", encoding="utf-8") as file:
                file.write(str(content))
        else:
            if "/" in url:
                directory=url.rsplit("/",1)[0]
                filename=url.rsplit("/",1)[1]
            else:
                directory=url
                filename=url
            filename=filename.replace(".html","")
            filename=filename+".txt"
            directoryPath=os.path.join(self.BASE_DIR_CRAWLER,directory)
            filepath=os.path.join(directoryPath,filename)
            if not os.path.exists(directoryPath):
                os.makedirs(directoryPath)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(str(content))

    def filter_allowed_urls(self,urls):
        filter_urls=set([])
        for url in urls:
            if not url.startswith("."):
                for rule in self.crawling_rules:
                    if rule[0].search(self.start_url+url):
                        filter_urls.add(url)
        if filter_urls:
            return filter_urls


url_pattern1="^(https://docs.python.org)/[0-9](.[0-9])/$"
url_pattern2="^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9-.]+/[a-zA-z0-9.-]*?$"
url_pattern3="^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9.-]+[/][A-Za-z0-9.-]+/[A-Za-z0-9.-]*$"

url_pattern1=re.compile(url_pattern1)
url_pattern2=re.compile(url_pattern2)
url_pattern3=re.compile(url_pattern3)

patterns=[
    (url_pattern1,"div.body table.contentstable"),
    (url_pattern2,""),
    (url_pattern3,"")
]
webgraber=WebGraber("https://docs.python.org/3.8/",patterns,2)

