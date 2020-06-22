import requests
from bs4 import BeautifulSoup as BS
import os
import random

BASE_DIR=os.getcwd()

class WebGraber:
    def __init__(self,url,version):
        self.url=url
        self.version=version
        self.all_topic_hrefs=[]



    def crawl(self):
        base_url=self.url+"/"+str(self.version)
        response = requests.get(base_url)
        bs_homePage = BS(response.text, 'html.parser')
        if response.status_code !=200:
            print(response.status_code)
            print("Error while extracting url. Please check your url and version number")
            return

        # create directory for pythonVersion and save home page file in it
        BASE_DIR=os.path.join(os.getcwd(),"python{}".format(self.version))
        if os.path.exists(BASE_DIR):
            #if path exists with the version number then add random number with filename
            BASE_DIR=BASE_DIR+"-"+str(random.randint(1,30))


        print("base name is ",BASE_DIR)
        os.mkdir(BASE_DIR)
        HOME_PAGE_PATH=os.path.join(BASE_DIR,"home.txt")
        with open(HOME_PAGE_PATH,"w",encoding="utf-8") as homeFile:
            homeFile.write(response.text)



        documentation_parts = bs_homePage.select_one("div.body table.contentstable")
        # extracting links from parts of documentation section
        for topic in documentation_parts.select('tr p.biglink a.biglink'):
            # creating list of urls of all topics
            self.all_topic_hrefs.append(topic['href'])
            # self.all_topic_urls.append(base_url+"/"+ topic['href'])







        # iterate over each url and get its page content
        for topic_href in self.all_topic_hrefs:
            topic_url=base_url+"/"+ topic_href

            print('Main category: ',topic_url)
            response = requests.get(topic_url)
            bs = BS(response.text, 'html.parser')

            #create sub directory and files only index file or root file will be create
            #in this loop other nested files will create in nested loop

            #extract directoryname from first part of url that is in topic_href like whatsnew,reference etc
            sub_directory_name=topic_href.rsplit('/',1)[0]

            #join the path with base dir python(version)
            SUB_DIR_PATH=os.path.join(BASE_DIR,sub_directory_name)
            os.mkdir(SUB_DIR_PATH)

            #extract filename from last part of url that is in topic_href
            sub_directory_file_name = self.filter_filename(topic_href.rsplit("/", 1)[1])

            #join the new subfile with subdirectory like (using >index, tutorial > index)
            SUB_DIR_FILE_PATH=os.path.join(SUB_DIR_PATH,sub_directory_file_name)
            with open(SUB_DIR_FILE_PATH,"w",encoding="utf-8") as sub_file:
                sub_file.write(response.text)



            # check if current page have sub_categories to visit
            if bs.select_one("div.toctree-wrapper.compound"):
                for sub_cateogry in bs.select('div.toctree-wrapper.compound > ul > li>a'):
                    # replace basename of url with the subcategory name
                    sub_cateogry_url = topic_url.replace(topic_url.rsplit('/', 1)[-1], sub_cateogry['href'])

                    print(" -crawling subcategory {}".format(sub_cateogry_url))
                    response_sub_category = requests.get(sub_cateogry_url)
                    bs_sub_category = BS(response.text, 'html.parser')

                    #generate name for sub text files.
                    sub_file_name=self.filter_filename(sub_cateogry['href'])
                    #set path for sub text files inside sub directory
                    sub_file_path=os.path.join(SUB_DIR_PATH,sub_file_name)

                    #write the sub_categories html pages on text file
                    with open(sub_file_path,"w",encoding="utf-8") as sub_file:
                        sub_file.write(response_sub_category.text)

            else:
                print("No subtree found")


    def filter_filename(self,filename):
        filename = filename.replace(".html", "")
        filename = filename + '.txt'
        return filename






if __name__ == '__main__':
    webgraber=WebGraber("https://docs.python.org",3.8)
    webgraber.crawl()

