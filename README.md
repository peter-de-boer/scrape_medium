# scrape_medium

This repository contains scripts to scrape the website medium.com and to analyze the results. 
I have written an article based on these results:
https://medium.com/@peterdb001/just-do-3-12-or-371-things-and-all-your-problems-are-solved-ad22911314a3

## Contents overview

The main part of this rep is a scrapy project.
For information on scrapy, see for example https://docs.scrapy.org/en/latest/intro/tutorial.html.
The main file (containing the spiders) is: `scrape_medium/spiders/medium.py`

The file main.py contains code to execute several scrapy commands.

The directory data contains output files that were generated by scrapy.

And finally, nthings.ipynb is a Jupyter notebook for analyzing the files under data.

## Medium.com 

Medium is a blogging platform containing millions of posts. 
You can search for posts, users, tags and publication by entering a search term. A search will give maximum 1000 results, split in chunks of 10, which are revealed by scrolling down. A search with the string "github features" will lead you to a URL like this

https://medium.com/search?q=github%20features

Basically all results can also be retrieved in json format, by adding a parameter format=json to the url.
It will return a json string, that is preceded by the following string (for security reasons):
```
])}while(1);</x>
```

Alternatively, ***all*** posts etc. could theoretically be found by parsing https://medium.com/sitemap/sitemap.xml.
That contains a list of xml files: new posts, users, tags and publication, one xml file for each day.
The xml file for a specific day of for examples posts contains the url's of all new posts from that day, etc.


## Spiders

The main spider in scrape_medium/spiders/medium.py is MediumSpider with name='medium'.
Usage:
```
scrapy crawl medium -a searchString=<mySearchString> -a fileName=<myFileName>
```

The parameter fileName is optional, default is ./out.csv.

This scrapy command will search for articles on medium.com with titles matching the searchString.
Results are appended to fileName. For each found article a line will be written:
```
searchString,id,title,createdAt,firstPublishedAt,readingTime,wordCount,totalClapCount
```

The spider MediumXmlSpider, with name = 'mediumxml', can be used to parse the xml file https://medium.com/sitemap/sitemap.xml, and the links therein.

**Warning** 
This spider could run a long time (weeks or months). 

The spider PublicationXmlSpider, with name = 'publicationxml', is similar to MediumXmlSpider. It will parse the xml files for the main publications on Medium that have their own domain.  

## main.py

Contains code to iterate over search terms and execute corresponding scrapy requests. 

## Data

The files under the data directory are the output of the scrapy calls in main.py.
```
different_kind_of_things.csv
different_kind_of_adjective_things.csv
different_kind_of_things_words.csv
```
The first file contains a list of articles with "1 thing", "2 things", ..., "1 lesson", "2 lessons", ... etc in the title.\
The second file contains a list of articles with "1 easy thing", "2 easy things", ..., "1 practical thing", ..., etc. in the title.\
In both files, the numbers go up to 1015.\
The third file contains a list of articles with "one thing", "two things", ..., "one lesson", "two lessons", ... etc in the title.\
In this file, the number goes up to twenty. 

## Jupyter notebook

The notebook nthings.ipynb reads in the files, converts the data to dataframes, and caluclates a few statistics.



