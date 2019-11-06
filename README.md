# scrape_medium

This repository contains scripts to scrape the website medium.com and to analyze the results.

## Contents overview

It contains a scrapy project. For information on scrapy, see for example https://docs.scrapy.org/en/latest/intro/tutorial.html
The main file under the scrape_medium is scrape_medium/spiders/medium.py. 

The file main.py contains code to execute several scrapy commands.

The directory data contains output files that were generated by scrapy.

And finally, nthings.ipynb is a Jupyter notebook for analyzing the files under data.

## Medium.com 

Medium is a blogging platform containing millions of posts. 
You can search for posts, users, tags and publication by entering a search term. A search will give maximum 1000 results, split in chunks of 10, which are revealed by scrolling down. A search will lead you to a URL like this

https://medium.com/search?q=github%20features

Basically all results can also be retrieved in json format, by adding a parameter format=json to the url.
It will return a json string, that is preceded by the following string.
```
])}while(1);</x>
```

Alternatively, ***all*** posts etc. can be found by parsing https://medium.com/sitemap/sitemap.xml.
That contains a list of xml files: new posts, users, tags and publication, one xml file for each day.
The xml file for a specific day of for examples posts contains the url's of all new posts from that day.


## Spiders

The main spider in scrape_medium/spiders/medium.py is MediumSpider with name='medium'.
Usage:
```
scrapy crawl medium -a searchString=<mySearchString> -a fileName=<myFileName>
```

The parameter fileName is optional, default is ./out.csv.

This scrapy command will search for articles on medium.com with titles matching the searchString.
Results are appeneded to fileName. For each found article a line will be written:
```
searchString,id,title,createdAt,firstPublishedAt,readingTime,wordCount,totalClapCount
```

The spider MediumXmlSpider, with name = 'mediumxml', can be used to parse the xml file https://medium.com/sitemap/sitemap.xml, and the links therein.

**Warning** 
This spider could run a long time (weeks). 

The spider PublicationXmlSpider, with name = 'publicationxml', is similar to MediumXmlSpider. It will parse the xml files for the main publications on Medium that have their own domain (
'https://medium.economist.com/'
'https://blog.coinbase.com/'
'https://uxdesign.cc/'
'https://thinkgrowth.org/'
'https://uxplanet.org/'
'https://blog.producthunt.com/'
'https://towardsdatascience.com/'
'https://byrslf.co/')

