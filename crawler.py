import requests
import sys
import re
import copy
import os
from bs4 import BeautifulSoup as BS


class WebGraber:
    def __init__(self,patterns,start_url,max_depth):
        self.start_url=start_url
        self.allowed_patterns=allowed_patterns
        self.max_depth=max_depth
        self.all_urls=set([])
        self.sub_level_urls=set([])
        self.temp_urls=set([])

    def crawl(self):
        self.all_urls.add(self.start_url)
        if self.max_depth==0:
            self.url_to_disk()
            return
        
        #section run if max_depth are more than 0
        self.sub_level_urls.add(self.start_url)
        initial_depth = 1
        #self.sub_levels_urls are to save the next level urls of current page
        while initial_depth <self.max_depth+ 1:
            #self.temp_urls are use to save temporary next levels urls and when iteration of sub_urls complete then we set new ursl from self.temp_url to self.sub_level_url
            self.temp_urls= set([])
            print("Level ", initial_depth)
            for sub_url in self.sub_level_urls:
                print(" \nVisiting URL =>", sub_url)
                response = download_url(sub_url)
                # fething urls (href) from the visiting page (sub_url)
                for url in response.find_all("a"):
                    fetch_url = url.get("href")

                    if not ".zip" in fetch_url and not ".tar.bz2" in fetch_url and not fetch_url.startswith(
                            '.') and not fetch_url.startswith("https"):
                        lastName = sub_url.rsplit("/", 1)[1]
                        if ".html" in lastName:
                            base_url = sub_url.rsplit("/", 1)[0]
                            fetch_url = base_url + "/" + fetch_url
                        else:
                            fetch_url = sub_url + fetch_url

                        self.add_url(fetch_url)

                    if fetch_url.startswith("https"):
                        self.add_url(fetch_url)

            self.sub_level_urls = copy.deepcopy(self.temp_urls)
            initial_depth = initial_depth + 1
        print("/n Extract url and save to disk")
        self.url_to_disk()

    def add_url(self,url):
        # filter allowed urls
        if self.allowed_urls(url):
            # add url to temp_url set only if that url is unvisit
            if url not in self.all_urls:
                print(" - sub url => ", url)
                self.temp_urls.add(url)
            self.all_urls.add(url)
    #extract all level urls in self.all_urls and save it to file
    def url_to_disk(self):
        for url in self.all_urls:
            #base_url can be self.start_url then you will only ge result of specific version that is in your self.start_url
            base = "https://docs.python.org/"
            _url = url.replace(base, "")
            dir = _url

            if dir.rsplit("/", 1)[1]:
                if ".html" in dir.rsplit("/", 1)[1]:
                    dir = dir.rsplit("/", 1)[0]

            if not os.path.exists(dir):
                os.makedirs(dir)
            if _url.rsplit("/", 1)[1]:
                filename = _url.rsplit("/", 1)[1]
            else:
                filename = dir.rsplit("/", 1)[0]
            filename = filename + ".txt"
            # create a filepath
            if dir[-1] == "/":
                FILEPATH = dir + filename
            else:
                FILEPATH = dir + "/" + filename

            print("Fecthing => ", url)
            res = self.download_url(url)
            print(" Filepath => ",FILEPATH)
            with open(FILEPATH, "w", encoding="utf-8") as file:
                file.write(str(res))

    def download_url(self,url):
        response = requests.get(url)
        if response.status_code != 200:
            print("Error while extracting url. Please check your url and version number")
            sys.exit()
        return BS(response.text, 'html.parser')

    def allowed_urls(self,url):
        for pattern in self.allowed_patterns:
            if pattern.search(url):
                return True
        return False

def download_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error while extracting url. Please check your url and version number")
        sys.exit()
    return BS(response.text, 'html.parser')



url_pattern1="^(https://docs.python.org)/[0-9](.[0-9])/$"
url_pattern2="^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9-.]+/?[a-zA-z0-9.-]*$"
url_pattern3="^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9.-]+[/][A-Za-z0-9.-]+/[A-Za-z0-9.-]*$"

url_pattern1=re.compile(url_pattern1)
url_pattern2=re.compile(url_pattern2)
url_pattern3=re.compile(url_pattern3)
allowed_patterns=[url_pattern1,url_pattern2,url_pattern3]


if __name__ == '__main__':
    webgraber=WebGraber(allowed_patterns,"https://docs.python.org/3.7/",2)
    webgraber.crawl()
