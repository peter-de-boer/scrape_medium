# -*- coding: utf-8 -*-
import scrapy
import json
import os
import datetime


class MediumSpider(scrapy.Spider):

    # searches articles on medium.com
    # with searchString in the title
    # writes results in fileName (csv format)

    name = 'medium'
    autothrottle_enabled=True  # just let's be nice :)

    def start_requests(self):

        # searchString can be passed by:
        #   scrapy crawl medium -a searchString=<mySearchString>

        # if searchString not passed, set to empty string
        try:
            self.searchString
        except:
            self.searchString=''
        self.queryString = self.searchString
        self.queryString.replace(" ", "%20")
        self.queryString = "%22" + self.queryString + "%22"

        # fileName can be passed by:
        #   scrapy crawl medium -a fileName=<myFileName>

        # if fileName not passed, set to empty string
        try:
            self.fileName
        except:
            self.fileName='out.csv'


        # medium.com has the feature that all request can be returned in json format
        # let's make use of it
        self.url = 'https://medium.com/search/posts?q=' + self.queryString + '&format=json'

        #set header info by looking to Network Tab in Developer tools
        self.headers= { \
        "sec-fetch-mode": "cors", \
        "origin": "https://medium.com", \
        "x-xsrf-token": "vbEzCL15XzVC", \
        "accept-language": \
            "en-US,en;q=0.9,de-AT;q=0.8,de;q=0.7,de-DE;q=0.6,nl;q=0.5,es;q=0.4", \
        "accept-encoding": "gzip, deflate, br", \
        "cookie": "__cfduid=d3cc845f3f167fb63f8ca64fdc5f214f51560932149; _ga=GA1.2.1982895133.1560932155; __stripe_mid=41d95cf0-513f-4623-b6e5-e32867d19757; uid=25e7d18c75b9; sid=1:sP5AuhHVHKNKcpU8tMTupiMDHNrGseuF0wZvzyF0ZiAc2FT6WGB66hGRzN8Nm+os; optimizelyEndUserId=25e7d18c75b9; lightstep_guid/medium-web=922d1a53bf8cdd76; lightstep_session_id=1985aa6824cab905; pr=1.25; tz=-120; lightstep_guid/lite-web=6f7d7a6542eccee4; _gid=GA1.2.357840978.1571076496; __cfruid=e73584466eb030d65d3266fea1dd8944eeba9f14-1571204694; xsrf=vbEzCL15XzVC; _parsely_session=^{^%^22sid^%^22:133^%^2C^%^22surl^%^22:^%^22https://medium.com/search/posts?q=Data^%^2520Science^%^22^%^2C^%^22sref^%^22:^%^22^%^22^%^2C^%^22sts^%^22:1571229069643^%^2C^%^22slts^%^22:1571224266008^}; _parsely_visitor=^{^%^22id^%^22:^%^22pid=0c5fb18c784e8df58bf0fa958c15b102^%^22^%^2C^%^22session_count^%^22:133^%^2C^%^22last_session_ts^%^22:1571229069643^}; sz=1055", \
        "x-obvious-cid": "web", \
        "x-client-date": "1571234072652", \
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36", \
        "content-type": "application/json", \
        "accept": "application/json", \
        "referer": "https://medium.com/search?q=Data^%^20Science", \
        "authority": "medium.com", \
        "sec-fetch-site": "same-origin"}


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

        # header should be consistent with the features written in parse method
        if writeHeader:
            header = 'searchString,id,title,createdAt,firstPublishedAt,readingTime,wordCount,totalClapCount\n'
            self.file.write(header)

        self.count=0

        yield scrapy.Request(self.url,callback=self.parse)

        #self.file.close()


    def storeFeatures(self, features):
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

        # iterate over results and store
        for article in payload['value']:

            # query returns not only original articles, but also responses
            # to filter them out: it seems that original articles have empty
            # values for this key:
            #   "inResponseToPostId": ""
            # the following key seems to be empty if inResponseToPostId is
            # empty as well and vice versa, so we do not check for it:
            #   "inResponseToMediaResourceId": "",

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
                # in excel
                readingTime = f"{article['virtuals']['readingTime']:.3f}"
                # features should be consistent with header written in
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

        body = json.dumps(paging['next'])
        yield scrapy.Request( self.url, method='POST', body=body, headers=self.headers, callback=self.parse )



class PublicationXmlSpider(scrapy.Spider):
    name = 'publicationxml'
    autothrottle_enabled=True  # just let's be nice :)

    def start_requests(self):

        # searchString can be passed by:
        #   scrapy crawl publicationxml -a ssearchString=<mySearchString>

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
    name = 'mediumxml'
    autothrottle_enabled=True  # just let's be nice :)

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

        for url in xlr:
            yield scrapy.Request(url, callback=self.parse_postxml)


    def parse_postxml(self, response):

        xxs = scrapy.selector.XmlXPathSelector(response)

        # namespace always needed for XmlXPathSelector
        xxs.register_namespace('n', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # get the list of urls
        xl=xxs.select('//n:url/n:loc/text()').extract()

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
