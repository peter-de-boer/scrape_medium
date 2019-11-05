import os

def callScrapy(searchString):
    callString = 'scrapy crawl medium -a searchString="' + searchString + '"'
    print(callString)
    os.system(callString)

"""
for nthings in range(1,1015):
    if nthings==1:
        noun = "thing"
    else:
        noun = "things"
    searchString = str(nthings) + " " + noun
    callScrapy(searchString)
"""

different_kind_of_things = ["things", "lessons", "ideas", "steps", "ways", "tips", "reasons",
          "tricks", "decisions"]
different_kind_of_things_singular = ["thing", "lesson", "idea", "step", "way", "tip", "reason",
          "trick", "decision"]
adjectives  = ["best", "worst", "easy", "practical", "top", "essential"]

"""
for things in different_kind_of_things:
    searchString = str(number) + " " + things
    callScrapy(searchString)
"""

"""
for things in different_kind_of_things:
    for adjective in adjectives:
        searchString = str(number) + " " + adjective + " " + things
        callScrapy(searchString)
"""



"""
for nthings in range(1, 1015):
    if nthings == 1:
        list_of_things = different_kind_of_things_singular
    else:
        list_of_things = different_kind_of_things
    for things in list_of_things:
        searchString = str(nthings) + " " + things
        callScrapy(searchString)
        for adjective in adjectives:
            searchString = str(nthings) + " " + adjective + " " + things
            callScrapy(searchString)
"""

numbers = ["one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
for number in numbers:
    if number == "one":
        list_of_things = different_kind_of_things_singular
    else:
        list_of_things = different_kind_of_things
    for things in list_of_things:
        searchString = number + " " + things
        callScrapy(searchString)
