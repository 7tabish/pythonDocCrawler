import requests
from bs4 import BeautifulSoup as BS
import os
import random
import re
BASE_DIR=os.getcwd()

class WebGraber:
    def __init__(self,url,version):
        self.url=url
        self.version=version
        self.all_topic_hrefs=[]
        #https://python.docs.org/3.7/optional1/optional2 .7 is also an optional
        self.regex = '^https://+[a-z]+[.]+[a-z]+[.]+[a-z]+[/]+[0-9]+(.?[0-9]?)+(/?[a-z]?)+([/]?)+([a-zA-z0-9]?)$'



    def crawl(self):
        base_url=self.url+"/"+str(self.version)
        #extrcting html content from url
        bs_homePage =self.extract_url(base_url)

        # create directory for pythonVersion and save home page file in it
        BASE_DIR=os.path.join(os.getcwd(),"python{}".format(self.version))
        if os.path.exists(BASE_DIR):
            #if path exists with the version number then add random number with filename
            BASE_DIR=BASE_DIR+"-"+str(random.randint(1,30))


        print("base name is ",BASE_DIR)
        os.mkdir(BASE_DIR)
        HOME_PAGE_PATH=os.path.join(BASE_DIR,"home.txt")

        self.create_text_file(HOME_PAGE_PATH,bs_homePage)



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
            bs = self.extract_url(topic_url)

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

            self.create_text_file(SUB_DIR_FILE_PATH,bs)




            # check if current page have sub_categories to visit
            if bs.select_one("div.toctree-wrapper.compound"):
                for sub_cateogry in bs.select('div.toctree-wrapper.compound > ul > li>a'):
                    # replace basename of url with the subcategory name
                    sub_cateogry_url = topic_url.replace(topic_url.rsplit('/', 1)[-1], sub_cateogry['href'])

                    print(" -crawling subcategory {}".format(sub_cateogry_url))
                    bs_sub_category =self.extract_url(sub_cateogry_url)


                    #generate name for sub text files.
                    sub_file_name=self.filter_filename(sub_cateogry['href'])
                    #set path for sub text files inside sub directory
                    sub_file_path=os.path.join(SUB_DIR_PATH,sub_file_name)

                    # write the sub_categories html pages on text file
                    self.create_text_file(sub_file_path,bs_sub_category)



            else:
                print("No subtree found")


    def filter_filename(self,filename):
        filename = filename.replace(".html", "")
        filename = filename + '.txt'
        return filename

    def extract_url(self,url):
        if re.search(self.regex,url):
            response = requests.get(url)
            if response.status_code != 200:
                print(response.status_code)
                print("Error while extracting url. Please check your url and version number")
                return
        else:
            print("url not match with pattern",url)
        return BS(response.text, 'html.parser')

    def to_string(self,html_content):
        return str(html_content)

    def create_text_file(self,file_path,html_content):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.to_string(html_content))





if __name__ == '__main__':
    webgraber=WebGraber("https://docs.python.org",3.6)
    webgraber.crawl()

