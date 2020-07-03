import requests
import sys
import re
import copy
import os
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
            print("Level ", initial_depth)
            for sub_url in self.sub_level_urls:
                print(" \nVisiting URL =>", sub_url)
                response = self.download_url(sub_url)
                # fething urls (href) from the visiting page (sub_url)
                for url in response.find_all("a"):
                    fetch_url = url.get("href")

                    if not "archives" in fetch_url:
                        fetch_url=urljoin(sub_url,fetch_url)
                        self.add_url(fetch_url)



            self.sub_level_urls = copy.deepcopy(self.temp_urls)
            initial_depth = initial_depth + 1
        print("/n Extract url and save to disk", len(self.all_urls))
        self.url_to_disk()

    def add_url(self, url):
        # filter allowed urls
        if self.check_allowed_domains(url):
            # add url to temp_url set only if that url is unvisit
            if url not in self.all_urls:
                self.temp_urls.add(url)
            self.all_urls.add(url)

    # extract all level urls in self.all_urls and save it to file
    def url_to_disk(self):
        for url in self.all_urls:
            try:
                parseUrl=urlparse(url)
                print("Fetching => ",url)
                response=self.download_url(url)
                if response:
                    if url[-1] == "/":
                        FILEPATH = parseUrl.path[1:-1]+".txt"
                    else:
                        FILEPATH = parseUrl.path[1:]+".txt"

                    if "/" in FILEPATH:
                        if not os.path.exists(os.path.dirname(FILEPATH)):
                            os.makedirs(os.path.dirname(FILEPATH))
                    #else no need to create directory direct file will create in root folder

                    with open(FILEPATH, "w", encoding="utf-8") as file:
                        file.write(str(response))
                    print("Filepath => ",FILEPATH)
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
        return False




domain1 = "^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9./-]+$"
domain2 = "^(https://www.python.org/)[a-zA-z0-9.-/]+$"



allowed_domain1 = re.compile(domain1)
allowed_domain2 = re.compile(domain2)


allowed_domains = [allowed_domain1, allowed_domain2]

if __name__ == '__main__':
    webgraber = WebGraber(allowed_domains, "https://docs.python.org/3.7/", 1)
    webgraber.crawl()
