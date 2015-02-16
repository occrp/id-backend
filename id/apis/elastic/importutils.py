import re

def luxembourg_date(filetext):
    '''
    Given the extracted text from the PDF of a Luxembourg gazette,
    return the date shown on the first page
    '''
    regex = re.compile('''
    #.*                 # anything
    #\W{1,999}         a bunch of whitespace
    (\d+\W\w+\W\w+)      # the date
    \W+                 # more whitespace
    SOMMAIRE           # the next recognisable line of text
    ''', re.VERBOSE|re.MULTILINE)
    match = regex.search(filetext, re.MULTILINE)
    if match:
        result = match.group(1).title()
    else:
        result = None
    return result


