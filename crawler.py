import requests
from bs4 import BeautifulSoup as BS
import os
import re
import random
import sys


class WebGraber():

    def __init__(self,url,version,css):
        self.base_url=url
        self.version=version
        self.css=css
        self.base_regex = re.compile("^(https://docs.python.org)/[0-9](.[0-9])/$")
        self.level1_regex = re.compile("^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9.-]+/[a-zA-z0-9.-]*?$")
        self.level2_regex = re.compile("^(https://docs.python.org)/[0-9](.[0-9])/[A-Za-z0-9.-]+[/][A-Za-z0-9.-]+/?$")
        self.home_page_urls=set([])
        self.sub_urls=set([])

    def crawl(self):
        
        self.base_url=self.base_url+str(self.version)+"/"
        if self.base_regex.search(self.base_url):
            bs = self.extract_url(self.base_url)
            # create directory for pythonVersion and save home page file in it
            BASE_DIR = os.getcwd()
            BASE_DIR=os.path.join(BASE_DIR,"crawler")
            if os.path.exists(BASE_DIR):
                # if path exists with the version number then add random number with filename
                BASE_DIR = BASE_DIR + "-" + str(random.randint(1, 30))
            os.mkdir(BASE_DIR)
            print("Crawler path: ",BASE_DIR)
            HOME_PATH = os.path.join(BASE_DIR, "home.txt")
            self.create_text_file(HOME_PATH, bs)

            if self.css:
                block=bs.select_one(self.css)
                if block:
                    for url in block.find_all("a"):
                        self.home_page_urls.add(url.get('href'))
                else:
                    print("no content found with this selector", self.css)
                    return
            else:
                for link in bs.findAll('a'):
                    if self.level1_regex.search(self.base_url + link.get('href')):
                        self.home_page_urls.add(link.get('href'))

            if len(self.home_page_urls)==0:
                print("No url found on page.")
                return

            for main_url in self.home_page_urls:
                print("------------------")
                print("level1 => ",self.base_url+main_url)
                self.sub_urls = set([])
                bs =self.extract_url((self.base_url + main_url))
                # href (main url) names can vry like settings/ settings.html or settings/index.html
                if "/" in main_url:
                    if main_url.rsplit("/", 1)[1]:  # it means url have index or home.html file after last /
                        # href => settings/index.html
                        # extract name from left side of / for directory (settings)
                        sub_directory_name = main_url.rsplit('/', 1)[0]
                        SUB_DIR_PATH = os.path.join(BASE_DIR, sub_directory_name)

                        if not os.path.exists(SUB_DIR_PATH):
                            os.mkdir(SUB_DIR_PATH)
                        # extract name from right of / to for filename (index.html)
                        sub_directory_file_name = self.filter_filename(main_url.rsplit("/", 1)[1])
                        SUB_DIR_FILE_PATH = os.path.join(SUB_DIR_PATH, sub_directory_file_name)
                        self.create_text_file(SUB_DIR_FILE_PATH, bs)
                    else:
                        # href => settings/
                        # file and directory name can be same

                        sub_directory_name = main_url.rsplit('/', 1)[0]
                        SUB_DIR_PATH = os.path.join(BASE_DIR, sub_directory_name)

                        if not os.path.exists(SUB_DIR_PATH):
                            os.mkdir(SUB_DIR_PATH)

                        sub_directory_file_name = self.filter_filename(main_url.rsplit("/", 1)[0])
                        SUB_DIR_FILE_PATH = os.path.join(SUB_DIR_PATH, sub_directory_file_name)
                        self.create_text_file(SUB_DIR_FILE_PATH, bs)
                else:
                    # href => settings.html
                    sub_directory_name = self.filter_filename(main_url)
                    SUB_DIR_PATH = os.path.join(BASE_DIR, sub_directory_name)

                    if not os.path.exists(SUB_DIR_PATH):
                        os.mkdir(SUB_DIR_PATH)

                    sub_directory_file_name = self.filter_filename(main_url)
                    SUB_DIR_FILE_PATH = os.path.join(SUB_DIR_PATH, sub_directory_file_name)
                    self.create_text_file(SUB_DIR_FILE_PATH, bs)

                # extracting urls from main_url response
                for link in bs.findAll('a'):
                    if "/" in main_url:
                        # main url be like settings/index.html
                        if main_url.rsplit("/", 1)[1]:
                            if link.get('href'):
                                if not link.get('href').startswith('.'):
                                    if self.level2_regex.search(
                                            self.base_url + main_url.replace(main_url.rsplit("/", 1)[1], link.get('href'))):
                                        self.sub_urls.add(link.get('href'))
                        # main url(href) be like  settings/
                        else:
                            if link.get('href'):
                                if not link.get('href').startswith('.'):
                                    if self.level2_regex.search(self.base_url + main_url + link.get('href')):
                                        # print("matching url i s",link.get('href'))
                                        self.sub_urls.add(link.get('href'))
                    # no / found in href (main_url) href => settings.html
                    else:
                        if link.get('href'):
                            if not link.get('href').startswith('.'):
                                if self.level2_regex.search(self.base_url + main_url +"/"+ link.get('href')):
                                    self.sub_urls.add(link.get('href'))

                # extract url for level 2 categories
                if self.sub_urls:
                    for sub_category in self.sub_urls:
                        if "/" in main_url:
                            if main_url.rsplit("/", 1)[1]:  # href(main_url be like) settings.html
                                sub_category_url = self.base_url + main_url.replace(main_url.rsplit("/", 1)[-1], sub_category)
                            else:  # href (main_url) be like settings/
                                sub_category_url = self.base_url + main_url + sub_category
                        # no / found in href
                        else:
                            sub_category_url = self.base_url + main_url +"/"+ sub_category
                        print("- crawling: ",sub_category_url)

                        bs_sub_category = self.extract_url(sub_category_url)
                        # create file name
                        sub_category_filename = self.filter_filename(sub_category)
                        sub_category_file_path = os.path.join(SUB_DIR_PATH, sub_category_filename)
                        self.create_text_file(sub_category_file_path, bs_sub_category)

    def create_text_file(self,file_path, html_content):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(html_content))

    def filter_filename(self,filename):
        eliminate_char = ['/', 'html']
        for char in eliminate_char:
            filename = filename.replace(char, "")
        filename = filename + '.txt'
        return filename
    def extract_url(self,url):
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print("Error while extracting {} ".format(url))
            sys.exit()
        return BS(response.text, 'html.parser')


if __name__ == '__main__':
    webgraber=WebGraber("https://docs.python.org/",3.7,"div.body table.contentstable")
    webgraber.crawl()
