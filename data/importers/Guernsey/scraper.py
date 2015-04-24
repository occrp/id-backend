#!/usr/bin/env python
#
#   Guernsey data importer. Doesn't actually work; first draft.
#
#
#
import requests
from BeautifulSoup import BeautifulSoup
import csv
import sys
import time
url = "https://www.greg.gg/webCompSearchDetails.aspx?id=HKG/irzleEQ=&r=0&crn=%d&cn=&rad=StartsWith&ck=False"
# https://www.greg.gg/webCompSearchDetails.aspx?id=HKG/irzleEQ=&r=0&crn=60224&cn=&rad=StartsWith&ck=False
# https://www.greg.gg/webCompSearchDetails.aspx?id=VebKHnR5twA=&r=0&crn=22000&cn=&rad=StartsWith&ck=False
# https://www.greg.gg/webCompSearchDetails.aspx?id=U6XYvIzVAMU=&r=1&crn=45&cn=&rad=StartsWith&ck=False

rownames = {
    "Register":                 "register",
    "Company Reg Number":       "id",
    "Company Name":             "name",
    "Company Type":             "type",
    "Company Classification":   "classification",
    "Company Status":           "status",
    "Registered Office Address":"address",
    "Economic Activity Type":   "activities",
    "Liability Type":           "liability",
    "Company Registered Date":  "registration_date",
    "Resident Agent Exempt?":   "agent_exempt",
    "Waive AGMs?":              "waive_agms",
    "Audit Exempt Annual?":     "audit_exempt_annual",
    "Audit Exempt Indefinite?": "audit_exempt_indefinite",
}

keys = rownames.values()
fh = open("guernsey.csv", "w+")
csv = csv.writer(fh)

for idn in xrange(1, 60224):
    company = {}

    html = requests.get(url % idn)
    
    soup = BeautifulSoup(html.content)
    table = soup.find("table", id="tblCompDetails")
    rows = table.findAll("tr")
    for row in rows:
        tds = row.findAll("td")
        x = tds[0].text.strip()
        if x in rownames:
            company[rownames[x]] = tds[1].text.strip()

        if len(tds) > 2:
            x = tds[2].text.strip()
            if x in rownames:
                company[rownames[x]] = tds[3].text.strip()

    dataline = [company[x].encode("utf-8") for x in keys]
    csv.writerow(dataline)

    print "\rDone %d." % idn,
    sys.stdout.flush()
    fh.flush()
    time.sleep(0.3)


print "\n\nALL DONE!!!\n\n"
fh.close()
