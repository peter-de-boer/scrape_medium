# -*- coding: utf-8 -*-
import scrapy
import json
import os
import datetime


class MediumSpider(scrapy.Spider):

    # searches articles on medium.com with searchString in the title
    # writes results in fileName (csv format)

    name = 'medium'
    autothrottle_enabled=True  # just let's be nice :)

    def start_requests(self):

        # fileName can be passed by:
        #   scrapy crawl medium -a fileName=<myFileName>

        # if fileName not passed, set to empty string
        try:
            self.fileName
        except:
            self.fileName='out.csv'

        # searchString can be passed by:
        #   scrapy crawl medium -a searchString=<mySearchString>

        # if searchString not passed, set to empty string
        try:
            self.searchString
        except:
            self.searchString=''

        # The searchString is used in two steps.
        # In the first step it is passed as a url parameter.
        # For this purposes, special characters need to be replaced.
        # For a full reference, see. e.g. https://krypted.com/utilities/html-encoding-reference/
        # We replace only spaces for now (add other characters when needed)
        # Furthermore we put the searchString between double quotes.
        # This is to ensure that in the case of multiple words (separated by
        # spaces), medium.com only returns titles that match the whole string.

        self.queryString = self.searchString
        self.queryString.replace(" ", "%20")
        self.queryString = "%22" + self.queryString + "%22"


        # medium.com has the feature that all request can be returned in json format
        # let's make use of it

        self.url = 'https://medium.com/search/posts?q=' + self.queryString + '&format=json'

        # In order to handle the pagination on medium.com (it will only return
        # 10 results at once), subsequent scrapy request need to be executed.
        # This needs to be done by POST request though.
        # For those requests, a header needs to be sent.
        # We need to define the header only once.
        # The folllowing is basically copied from the header info in Network Tab in Developer tools
        # in Chrome while browsing medium.com.

        self.headers= {}


        # open file for appending
        # if file did not exist yet, write header

        if os.path.exists(self.fileName) and not os.path.isfile(self.fileName):
            print("ERROR: ", self.fileName, " is not a file")
            return
        writeHeader = not os.path.exists(self.fileName)
        try:
            self.file = open(self.fileName, 'a', encoding="utf-8")
        except IOError as x:
            print('error ', x.errno, ',', x.strerror)
            return

        # csv header should be consistent with the features written in parse method
        if writeHeader:
            header = 'searchString,id,title,createdAt,firstPublishedAt,readingTime,wordCount,totalClapCount\n'
            self.file.write(header)

        self.count=0

        yield scrapy.Request(self.url,callback=self.parse)

        # Closing the file explicitly leads to problems related to multiple 
        # open/close calls due to subsequent scrapy requests.
        # So do not close explicitly, it will be automatically closed when the script ends

        #self.file.close()


    def storeFeatures(self, features):
        # write features list as a comma separated line
        stringToWrite = ''
        for feature in features:
            stringToWrite = stringToWrite + str(feature) + ','
        stringToWrite = stringToWrite[:-1] + '\n'
        self.file.write(stringToWrite)

    def getDateTime(self, milliseconds):
        #convert milliseconds to datetime string
        date = datetime.datetime.fromtimestamp(milliseconds/1000.0)
        return date.strftime('%Y-%m-%d %H:%M:%S')

    def parse(self, response):

        # get the text from the response

        response_data=response.text

        # strip of security code from json response

        response_split=response_data.split("while(1);</x>")
        response_string=response_split[1]

        # now convert the json string to true json object

        response_json=json.loads(response_string)

        # check if we have a valid non-empty result
        # if not valid, just return

        if 'payload' not in response_json:
            return
        payload = response_json['payload']

        if 'value' not in payload:
            return

        # iterate over results and store

        for article in payload['value']:

            # The query returns not only original articles, but also responses to
            # articles.
            # To filter them out: it seems that original articles have empty
            # values for this key:
            #   "inResponseToPostId": ""
            #
            # Furthermore, the query also return articles where the subtitle
            # matches the searchString (this is just how medium.com search
            # works).
            # To filter these out, check explicitly if the searchString indeed
            # occurs in the title.

            if article["inResponseToPostId"]=="" and self.searchString.lower() in article["title"].lower():

                self.count=self.count+1
                print(self.count, article['id'], article['title'])

                # store article
                # first remove the following characters from title in order to
                # avoid problems with those characters in csv:
                #   ; , " ' + . : ? \n
                title = article['title'].replace('"','')
                title = title.replace(',','')
                title = title.replace("'",'')
                title = title.replace(";",'')
                title = title.replace("+",'')
                title = title.replace(".",'')
                title = title.replace(":",'')
                title = title.replace("?",'')
                title = title.replace("\n",'')
                # convert milliseconds to datetime
                createdAt = self.getDateTime(article['createdAt'])
                firstPublishedAt = self.getDateTime(article['firstPublishedAt'])
                # format readingTime so fractions won't be converted to dates
                # in excel, in case you'd like to open the csv in excel
                readingTime = f"{article['virtuals']['readingTime']:.3f}"
                # featuresToStore should be consistent with header written in
                # start_requests method
                featuresToStore = [ \
                                   self.searchString, \
                                   article['id'], \
                                   title, \
                                   createdAt, \
                                   firstPublishedAt, \
                                   readingTime, \
                                   article['virtuals']['wordCount'], \
                                   article['virtuals']['totalClapCount'] \
                                  ]
                self.storeFeatures(featuresToStore)

        # handle paging
        if not 'paging' in payload:
            return
        paging=payload['paging']
        if not 'next' in paging:
            return

        # a next page is there, create a new request to get it

        body = json.dumps(paging['next'])
        yield scrapy.Request( self.url, method='POST', body=body, headers=self.headers, callback=self.parse )




class PublicationXmlSpider(scrapy.Spider):

    # searches on publications on medium with their own domain
    # by parsing the xml file https://<publication domain/sitemap/sitemap.xml
    # this is not finished due to problem swith xml parsing (see
    # MediumXmlSpider)

    name = 'mediumxml'
    name = 'publicationxml'
    autothrottle_enabled=True  # just let's be nice :)

    def start_requests(self):

        # searchString can be passed by:
        #   scrapy crawl publicationxml -a searchString=<mySearchString>

        try:
            self.searchString
        except:
            #self.searchString="Data%20Science"
            self.searchString=''

        # create a new csv file
        # TODO

        self.count=0

        urls = [  \
            'https://medium.economist.com/', \
            'https://blog.coinbase.com/', \
            'https://uxdesign.cc/', \
            'https://thinkgrowth.org/', \
            'https://uxplanet.org/', \
            'https://blog.producthunt.com/', \
            'https://towardsdatascience.com/', \
            'https://byrslf.co/'
       ]

        for url in urls:
            urlsitemap = url + 'sitemap/sitemap.xml'
            yield scrapy.Request(urlsitemap, callback=self.parse, \
                                 meta={'url': url})



    def parse(self, response):

        xxs = scrapy.selector.XmlXPathSelector(response)

        # namespace always needed for XmlXPathSelector
        xxs.register_namespace('n', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # get the list of urls
        xl=xxs.select('//n:url/n:loc/text()').extract()

        # filter out .../tagged/ urls; they contains articles posted elsewhere
        urltagged = response.meta['url'] + 'tagged/'
        xlr =[u for u in xl if urltagged not in u]

        print(len(xlr), response.meta['url'])



class MediumXmlSpider(scrapy.Spider):

    # searches on medium.com with searchString in the title
    # by parsing the xml file https://medium.com/sitemap/sitemap.xml
    # this is not completely finished
    # usefulness is limited anyway: due to the number of requests and the fact
    # that a download_delay between requests is needed, a typcial search would
    # take weeks or months....

    name = 'mediumxml'
    autothrottle_enabled=True  # just let's be nice :)

    # set a sufficient delay between request, else medium.com will deny
    # requests

    custom_settings = {
        'DOWNLOAD_DELAY': 0.50
    }

    def start_requests(self):

        # searchString can be passed by:
        #   scrapy crawl mediumxml -a ssearchString=<mySearchString>

        try:
            self.searchString
        except:
            #self.searchString="Data%20Science"
            self.searchString=''

        # create a new csv file
        f=open("articles.csv", "w+", encoding="utf-8")
        f.write("id,title,createdAt,readingTime,totalClapCount\n")
        f.close()

        self.count=0

        urls=['https://medium.com/']

        for url in urls:
            urlsitemap = url + 'sitemap/sitemap.xml'
            yield scrapy.Request(urlsitemap, callback=self.parse, \
                                 meta={'url': url})



    def parse(self, response):

        xxs = scrapy.selector.XmlXPathSelector(response)

        # namespace always needed for XmlXPathSelector
        xxs.register_namespace('n', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # get the list of xml links
        xl=xxs.select('//n:sitemap/n:loc/text()').extract()

        # select .../posts/ urls
        xmlposts = response.meta['url'] + 'sitemap/posts/'
        xlr =[u for u in xl if xmlposts in u]

        # now parse the post xml files
        for url in xlr:
            yield scrapy.Request(url, callback=self.parse_postxml)


    def parse_postxml(self, response):

        xxs = scrapy.selector.XmlXPathSelector(response)

        # namespace always needed for XmlXPathSelector
        xxs.register_namespace('n', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # get the list of urls
        xl=xxs.select('//n:url/n:loc/text()').extract()

        # for each post, get the corresponding json data and parse them
        for url in xl:
            urljson = url + '?format=json'
            yield scrapy.Request(urljson, callback=self.parse_json)


    def parse_json(self, response):

        response_data=response.text
        # strip of security code from json response
        response_split=response_data.split("while(1);</x>")
        response_string=response_split[1]

        # now convert the json string to true json object
        response_json=json.loads(response_string)

        # check if we have a valid non-empty result
        if 'payload' not in response_json:
            return
        payload = response_json['payload']

        if 'value' not in payload:
            return

        article=payload['value']
        if article["inResponseToPostId"]=="" and self.searchString.lower() in article["title"].lower():
            # store article
            f=open("articles.csv", "a+", encoding="utf-8")
            self.count=self.count+1
            print(self.count, article['id'], article['title'])
            # remove , and " and ' from title in order to avoid problems with those
            # characters in csv
            title = article['title'].replace('"','')
            title = title.replace(',','')
            title = title.replace("'",'')
            f.write(str(article['id']) + ',' + title + ',' + \
                    str(article['createdAt']) + ',' + \
                    str(article['virtuals']['readingTime']) + ',' + \
                    str(article['virtuals']['totalClapCount']) + '\n')
            f.close()
            #print(json.dumps(article, indent=4, sort_keys=True))
            #return
