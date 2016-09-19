#!/usr/bin/env python
#
# GDrive files stats
#

import pickle

mime_types = {}

def sizeof_fmt(num, suffix='B'):
     for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
         if abs(num) < 1024.0:
             return "%3.1f%s%s" % (num, unit, suffix)
         num /= 1024.0
     return "%.1f%s%s" % (num, 'Yi', suffix)


for f in filelist:
     if f['mimeType'] not in mime_types:
             mime_types[f['mimeType']] = {'size': 0, 'count': 0}
     mime_types[f['mimeType']]['count'] += 1
     if 'fileSize' in f:
             mime_types[f['mimeType']]['size'] += int(f['fileSize']) 

for mt in mime_types:
    print 'Type: %20s; files: %d; size: %d' % (mt, mime_types[mt]['count'], mime_types[mt]['size'])


if __name__ == "__main__":
    
    try:
        # requried args
        script, filelist_file_base = sys.argv
    except:
        print("\nRun via:\n\t%s </path/to/legacy-investigative-dashboard> <imported-files-list-file-path> [--keep]\n" % sys.argv[0])
        print("Temporary files are being saved in:\n\t/tmp/id_gdrive_downloads/root/<individual-filenames>\n\nOptional --keep parameter makes the script not delete the downloaded files after Podaci import.\n")
        sys.exit()