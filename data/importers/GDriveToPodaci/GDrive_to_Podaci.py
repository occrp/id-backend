#!/usr/bin/env python
#
# Google Drive to Podaci importer
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


# getting a string from a textfile
def file_to_str(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, 'r') as f:
        return f.read()
      
      
# getting the pickled data from a pickle file
def get_pickled_data(picklepath):
    with open(picklepath, 'rb') as picklefile:
        return pickle.load(picklefile)


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

    #http = httplib2.Http(cache=memcache)
    http = httplib2.Http()
    http = credentials.authorize(http)

    try:
        return build('drive', 'v2', http=http)
    except NotImplementedError:
        raise DriveError(_('Your Google Drive private key must be in "PEM" format.'))
    except client.AccessTokenRefreshError:
        raise DriveError(_('Error refreshing Google Drive access token. Check your settings and try again.'))


# get contents of a folder
def list_folder_contents(service, folder_id):
    
    print 'Listing folder: %s' % folder_id
    file_list = []
    
    page_token = None
    while True:
        print '+-- in while loop'
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            
            # folder GET
            print '+-- running service.children()...'
            children = service.children().list(folderId=folder_id, **param).execute()

            # contents
            print '+-- iterating through the children'
            for child in children.get('items', []):
                print '     +-- file id: %s' % (child['id'])
            file_list.extend(children.get('items', []))
                
            # paging
            page_token = children.get('nextPageToken')
            if not page_token:
                break
        
        # whoops!
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break
    
    # return the file lits
    return file_list


def get_file_metadata(service, file_id):
    """Print a file's metadata.

    Args:
      service: Drive API service instance.
      file_id: ID of the file to print metadata for.
    """
    try:
        f = service.files().get(fileId=file_id).execute()
        return f
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def download_file(service, file_id, local_fd):
    """Download a Drive file's content to the local filesystem.

    Args:
      service: Drive API Service instance.
      file_id: ID of the Drive file that will downloaded.
      local_fd: io.Base or file object, the stream that the Drive file's
          contents will be written to.
    """
    request = service.files().get_media(fileId=file_id)
    media_request = apihttp.MediaIoBaseDownload(local_fd, request)

    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return
        if download_progress:
            print '\r     +-- download progress: %d%%' % int(download_progress.progress() * 100),
            sys.stdout.flush()
        if done:
            print '\r     +-- done.                                   '
            sys.stdout.flush()
            return


def handle_folder_id(service, folder_id):
    file_ids_list = list_folder_contents(service, folder_id)
    
    # get file metadata
    file_info_list = []
    for f in file_ids_list:
        file_info_list.append(get_file_metadata(service, f['id']))
        
    # whoohoo, we have a file list!
    # interesting bits are:
    # - mimeType
    # - id
    # - title
    # - originalFilename
    # - md5Checksum
    
    # make sure the output directory exists and is a directory
    # name: /tmp/id_gdrive_downloads/<folder-id>/
    dfolder = os.path.join('/tmp/id_gdrive_downloads/', folder_id)
    if not os.path.exists(dfolder):
        os.makedirs(dfolder)
    
    # let's download some files!
    print 'Retrieving files...'
    for f in file_info_list:
        
        print '+-- file: %s (md5: %s)' % (f['originalFilename'], f['md5Checksum'])
        
        # filename
        fname = os.path.join(dfolder, f['originalFilename'])
        
        # if the file exists...
        if os.path.isfile(fname):
            print '     +-- file exists, checking md5...'
            with open(fname, 'rb') as dfile:
                if hashlib.md5(dfile.read()).hexdigest() == f['md5Checksum']:
                    print '     +-- checksums match, not downloading.'
                    continue
                else:
                    print '     +-- checksums do not match, downloading...'
            
        # download the bugger
        with open(fname, 'wb') as dfile:
            download_file(service, f['id'], dfile)


if __name__ == "__main__":
    
    try:
        script, idpath, drivefolderids_path = sys.argv
    except ValueError:
        print("\nRun via:\n    %s </path/to/legacy-investigative-dashboard> <drive-folder-ids-file-path>\n" % sys.argv[0])
        print("Temporary files are being saved in /tmp/id_gdrive_downloads/<folder-id>/<individual-filenames>")
        sys.exit()
    
    # make sure we have the config available
    sys.path.append(os.path.abspath("%s/app/config/" % idpath))
    from production import config
    
    # pickled drive folder ids are required
    print "Loading pickled drive folder ids from %s..." % drivefolderids_path
    try:
        drivefolderids = get_pickled_data(drivefolderids_path)
        print '+-- loaded %d drive folder ids' % len(drivefolderids)
    except e:
        print '+-- error loading pickled drive folder ids: %s' % e
        sys.exit(1)
    
    # create the damn gdrive service
    service = create_system_service()
    
    # get folder contents
    for folder in drivefolderids:
        # let's handle a google drive folder, shall we?
        handle_folder_id(service, drivefolderids[folder])