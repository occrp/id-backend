#!/usr/bin/env python

'''
Walk through an apache directory listing,
providing a list of all files there.
'''

import sys
import urllib
import urlparse
import re
import traceback
import random
import elastic

parse_re = re.compile('href="([^"]*)".*(..-...-.... ..:..).*?(\d+[^\s<]*|-)')
          # look for          a link    +  a timestamp  + a size ('-' for dir)

def iterate_apache_dir(url):
    '''
    generator to recursively walk an apache directory listing,
    returning absolute URLs for all the files (not all the directories)
    '''
    try:
        html = urllib.urlopen(url).read()
    except IOError, e:
        print 'error fetching %s: %s' % (url, e)
        raise StopIteration
    if not url.endswith('/'):
        url += '/'
    files = parse_re.findall(html)
    dirs = []

    for name, date, size in files:
        if name.endswith('/'):
            dirs += [name]
        else:
            yield urlparse.urljoin(url, name)

    for dir in dirs:
        for i in iterate_apache_dir(url + dir):
            yield i


def recursive_upload(baseurl, tags, index, logfn, sample=None, **kwargs):
    lf = open(logfn, 'a')
    for url in iterate_apache_dir(baseurl):
        if sample: # lets us take a few docs for testing
            if random.randint(1,sample) != sample:
                lf.write('SKIP: %s\n' % url)
                continue
        try:
            ul = elastic.upload_from_url(
                url,
                tags=tags,
                index=index,
                **kwargs
                )
            lf.write('OK:   %s\n' % url)
        except Exception:
            lf.write('FAIL: %s\n' % url)
            lf.write(traceback.format_exc())
