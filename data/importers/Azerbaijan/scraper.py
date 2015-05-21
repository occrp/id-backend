#!/usr/bin/env python
#
#  Azerbaijan President's movements -- event scraper
#
#
#
import requests
from BeautifulSoup import BeautifulSoup
import csv
import sys
url = "http://en.president.az/news/events?page=%d"

fh = open("aliyev-events.csv", "w+")
csv = csv.writer(fh)

for idn in xrange(1, 133):
    html = requests.get(url % idn)
    
    soup = BeautifulSoup(html.content)
    ev = soup.findAll("div", attrs={"class": "article_item"})
    for event in ev:
        datetime = event.find("div", attrs={"class":"datetime"}).text.strip()
        date, time = datetime.split(",")
        description = event.find("div", attrs={"class":"article_name"}).text.strip()
        dataline = [unicode(date.strip()), unicode(time.strip()), unicode(description).encode("utf-8")]
        csv.writerow(dataline)

    print "\rDone %d." % idn,
    sys.stdout.flush()
    fh.flush()


print "\n\nALL DONE!!!\n\n"
fh.close()
