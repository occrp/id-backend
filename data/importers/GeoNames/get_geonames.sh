#!/bin/bash

wget http://download.geonames.org/export/dump/allCountries.zip
wget http://download.geonames.org/export/dump/countryInfo.txt
unzip allCountries.zip
mkdir output
python gen_csvs.py
