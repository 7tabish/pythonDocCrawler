import requests
import sys
import re
import copy
import os
import shutil
from bs4 import BeautifulSoup as BS
from urllib.parse import urljoin,urlparse

class WebGraber:
    def __init__(self, allowed_domains, start_url, max_depth):
        self.start_url = start_url
        self.allowed_domains = allowed_domains
        self.max_depth = max_depth
        self.all_urls = set([])
        self.sub_level_urls = set([])
        self.temp_urls = set([])
        self.js_visited_urls=[]
        self.static_visisted_urls=[]
    def crawl(self):
        self.all_urls.add(self.start_url)
        if self.max_depth == 0:
            self.url_to_disk()
            return

        # section run if max_depth are more than 0
        self.sub_level_urls.add(self.start_url)
        initial_depth = 1
        # self.sub_levels_urls are to save the next level urls of current page
        while initial_depth < self.max_depth + 1:
            # self.temp_urls are use to save temporary next levels urls and when iteration of sub_urls complete then we set new ursl from self.temp_url to self.sub_level_url
            self.temp_urls = set([])
            for sub_url in self.sub_level_urls:
                response = self.download_url(sub_url)
                # fething urls (href) from the visiting page (sub_url)
                for url in response.find_all("a"):
                    fetch_url = url.get("href")

                    if not "archives" in fetch_url and not "tar" in fetch_url\
                        and not "msi" in fetch_url and not "pkg" in fetch_url and not "zip" in fetch_url:
                        fetch_url=urljoin(sub_url,fetch_url)
                        self.add_url(fetch_url)



            self.sub_level_urls = copy.deepcopy(self.temp_urls)
            initial_depth = initial_depth + 1

        self.url_to_disk()

    def add_url(self, url):
        # filter allowed urls
        # print("sub => ",url)
        if self.check_allowed_domains(url):
            # add url to temp_url set only if that url is unvisit
            if url not in self.all_urls:
                self.temp_urls.add(url)
                self.all_urls.add(url)



    def url_to_filepath(self,url):
        if self.check_allowed_domains(url):
            filePath = urlparse(url).path
            directory = os.path.dirname(filePath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            return filePath

    def downlaod_image(self,url,filepath):
        print("Downloding image => ",filepath)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    def save_page(self,filepath,content):
        try:
            with open(filepath,"w",encoding="utf-8") as file:
                file.write(str(content))
        except Exception as e:
            print(e)


    # extract all level urls in self.all_urls and save it to file
    def url_to_disk(self):
        for url in self.all_urls:
            try:
                print("Visiting url => ",url)
                parseUrl=urlparse(url)
                response=self.download_url(url)
                if response:
                    if url[-1] == "/": #if path be like base/page1/page2/
                        FILEPATH =os.path.join(parseUrl.path,"index.html")
                    elif not ".html" in url:
                        FILEPATH = parseUrl.path[1:]+".html"
                    else:#aready have .html in path
                        FILEPATH=parseUrl.path
                    if "/" in FILEPATH:
                        if not os.path.exists(os.path.dirname(FILEPATH)):
                            os.makedirs(os.path.dirname(FILEPATH))
                    #else no need to create directory direct file will create in root folder
                    self.save_page(FILEPATH,response)



                    #fetching css and icons
                    for css in response.find_all("link"):
                        style_url=urljoin(url,css['href'])
                        if not style_url in self.static_visisted_urls:
                            filepath=self.url_to_filepath(style_url)
                            if filepath:
                                if "icon" in css['rel']:
                                    self.downlaod_image(style_url,filepath)
                                if "stylesheet" in css['rel']:
                                    style_response=self.download_url(style_url)
                                    print("Save static asset => ",filepath)
                                    self.save_page(filepath,style_response)
                                self.static_visisted_urls.append(style_url)

                    #fetching images
                    for image in response.find_all("img"):
                        img_url = urljoin(url, image['src'])
                        if url not in self.static_visisted_urls:
                            filepath = self.url_to_filepath(img_url)
                            if filepath:
                                self.downlaod_image(img_url, filepath)
                            self.static_visisted_urls.append(img_url)

                    #fetching js
                    for javascript in response.find_all("script"):
                        js_string=str(javascript)
                        #we may found <script> tag but some of them not containing src tag.
                        if not js_string[:8]=="<script>":
                            js_url = urljoin(url, javascript['src'])
                            if not js_url in self.js_visited_urls:
                                js_response=self.download_url(js_url)
                                filepath = self.url_to_filepath(js_url)
                                print("javascript path => ", filepath)
                                if filepath:
                                    self.save_page(filepath,js_response)
                                self.js_visited_urls.append(js_url)
                    print("------------------------------------")
            except Exception as error:
                    print("error: ",error)

    def download_url(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print("Error while extracting url. Please check your url and version number",url)
            return False
        return BS(response.text, 'html.parser')

    def check_allowed_domains(self, url):
        for domain in self.allowed_domains:
            if domain.search(url):
                return True







domain1='^(https://nodejs.org/docs)/[A-Za-z0-9./-]+$'
domain2='^(https://nodejs.org/en/docs)/[A-Za-z0-9./-]+$'
domain3='^(https://nodejs.org)/[A-Za-z0-9./-]+$'

allowed_domain1 = re.compile(domain1)
allowed_domain2 = re.compile(domain2)
allowed_domain3=re.compile(domain3)

allowed_domains = [allowed_domain1, allowed_domain2,allowed_domain3]

if __name__ == '__main__':
    webgraber = WebGraber(allowed_domains, "https://nodejs.org/en/docs/", 1)
    webgraber.crawl()
