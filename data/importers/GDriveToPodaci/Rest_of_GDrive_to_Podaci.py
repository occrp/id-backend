#!/usr/bin/env python
#
# Google Drive to Podaci importer -- non Ticket-related files
#
# that's kind of needed too:
# pip install pycrypto
# pip install --upgrade google-api-python-client

import sys
import os
import httplib2
import pickle
import hashlib
from apiclient import errors
from apiclient import http as apihttp
from apiclient.discovery import build
from oauth2client import client

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
sys.path.append(os.path.abspath("../../../"))
from id.models import *
from ticket.models import *
# from podaci import File, Tag, FileSystem

from GDrive_to_Podaci import handle_gdrive_file, podacify_file
from pprint import pprint

imported_files = {}


def create_system_service():
    """
    Builds and returns a Drive service object authorized with the app's
    service account.
    """
    credentials = client.SignedJwtAssertionCredentials(
        config['drive_service_account'],
        config['drive_private_key'],
        scope='https://www.googleapis.com/auth/drive',
        prn=config['drive_owner_account']
    )

    #http = httplib2.Http(cache="/tmp/id_gdrive_downloads/.cache")
    http = httplib2.Http()
    http = credentials.authorize(http)

    try:
        return build('drive', 'v2', http=http)
    except NotImplementedError:
        raise DriveError(_('Your Google Drive private key must be in "PEM" format.'))
    except client.AccessTokenRefreshError:
        raise DriveError(_('Error refreshing Google Drive access token. Check your settings and try again.'))


def dump_pickled_filelist(files, i):
    try:
        with open('%s.%d' % (gdrive_filelist_file, i), 'wb') as gflfile:
            pickle.dump(files, gflfile)
        print "Dumped %d files metadata to %s." % (len(files), gdrive_filelist_file)
    except:
        print 'Dumping %d files metadata to %s has failed!..' % (len(files), gdrive_filelist_file)


def retrieve_all_files(service, dfolder):
    """Retrieve a list of File resources.

    Args:
      service: Drive API service instance.
    Returns:
      List of File resources.
    """
    print 'Retrieving file list for the GDrive root folder...'
    result = []
    i = 0
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            param['maxResults'] = 1000
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            print '+-- %d files metadata retrieved (%d in total)...' % (len(files['items']), len(result))
            # make sure we won't lose them in case of a fsckup
            dump_pickled_filelist(files['items'], i)
            for f in files['items']:
                if 'google-apps.folder' in f['mimeType']:
                    continue
                
                if not 'originalFilename' in f:
                    f['originalFilename'] = f['title'].replace(os.sep, '_')
                    
                if f['id'] in imported_files:
                    print '+-- file: %s already imported' % f['originalFilename']
                    continue
                
                # what if the id is different but the md5 and filename is the same?
                f['localPath'] = os.path.join(dfolder, f['originalFilename'])
                print '+-- file: %s (md5: %s)' % (f['originalFilename'], f['md5Checksum'])

                handle_gdrive_file(service, f)
                # handle the podaci side of things
                podacify_file(imported_files, f)
            # move on to the next page
            page_token = files.get('nextPageToken')
            if not page_token:
                break
            i = i+1
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break
    print '+-- done. %d files retrieved in total.' % len(result)
    return result


if __name__ == "__main__":

    try:
        # requried args
        script, idpath, imported_files_file = sys.argv
    except:
        print("\nRun via:\n\t%s </path/to/legacy-investigative-dashboard> <imported-files-list-file-path>\n" % sys.argv[0])
        print("Pickled GDrive file metadata are being saved in:\n\t/<imported-file-list-file-containing-folder>/GDrive.filelist.<n>\n...where n is the consecutive number of data file (one per GDrive API call, max. 1000 files returned per call)")
        sys.exit()

    # pickle and save the result
    gdrive_filelist_file = os.path.join(
        os.path.dirname(
          os.path.abspath(
            imported_files_file
          )
        ), 'GDrive.filelist')

    # the "d" is silent
    print "Setting up django..."
    django.setup()

    # make sure we have the config available
    sys.path.append(os.path.abspath("%s/app/config/" % idpath))
    from production import config

    # files already imported
    print "Loading imported files data..."
    try:
        with open(imported_files_file, 'rb') as iffile:
            imported_files = pickle.load(iffile)
        print '+-- loaded %d imported file data from %s' % (len(imported_files), imported_files_file)
    except:
        print "+-- warning, no imported file data loaded, tried from %s." % imported_files_file


    # user
    # u = Profile.objects.get(email='admin@example.com') # FIXME
    # # podaci filesystem
    # fs = FileSystem(user=u)
    # # podaci tickets meta tag
    # try:
    #     metatag = fs.get_tag('Rest_Of_GDrive_Meta_Tag')
    # except:
    #     metatag = Tag(fs)
    #     metatag.id = 'Rest_Of_GDrive_Meta_Tag'
    #     metatag.create('Rest Of GDrive Meta Tag')

    # create the damn gdrive service
    service = create_system_service()

    dfolder = os.path.join('/tmp/id_gdrive_downloads/rest')
    if not os.path.exists(dfolder):
        os.makedirs(dfolder)

    # handling the keyboard interrupt gracefully
    try:
        files = retrieve_all_files(service, dfolder)
    except KeyboardInterrupt:
        print 'KeyboardInterrupt caught, exitin gracefully'
    #except Exception as e:
    #   print 'Exception caught: %s (%s); exiting gracefully' % (e, type(e))

    #dump_pickled_filelist(files)

    # have we actually saved any files?
    if imported_files:
        try:
            with open(imported_files_file, 'wb') as iffile:
                pickle.dump(imported_files, iffile)
            print "Dumped %d file ids to %s." % (len(imported_files), imported_files_file)
        except:
            print 'Dumping %d file ids %s has failed!..' % (len(imported_files), imported_files_file)
