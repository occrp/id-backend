#!/usr/bin/env python
#
# Google Drive to Podaci importer -- Ticket-related files only!
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
from podaci.models import PodaciFile as File

imported_files = {}

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

    #http = httplib2.Http(cache="/tmp/id_gdrive_downloads/.cache")
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
            print '\r     +-- downloaded.                                   '
            sys.stdout.flush()
            return


def handle_gdrive_file(service, f):
    # if the file exists...
    if os.path.isfile(f['localPath']):
        print '     +-- file exists, checking md5...'
        with open(f['localPath'], 'rb') as dfile:
            if hashlib.md5(dfile.read()).hexdigest() == f['md5Checksum']:
                print '     +-- checksums match, not downloading.'
                return False
            else:
                print '     +-- checksums do not match, downloading...'

    # download the bugger
    with open(f['localPath'], 'wb') as dfile:
        download_file(service, f['id'], dfile)
    return True


def podacify_file(imported_files, f, ticket=None):
    print '+-- podacifying...'
    ### FILE
    # create the file
    pfile = File.create_from_path(f['localPath'], ticket=ticket)

    # put the id into the imported_files list, to be pickled and saved to a file later
    # legacy Google ID of the file itself, needed for later downloading of files that were not in any ticket-related folder
    imported_files[f['id']] =  {
      'folder'      : f.get('legacyGoogleFolderId'), # legacy Google Folder ID the file was in
      'md5Checksum' : f['md5Checksum']
    }

    if ticket is not None:
        # set permissions, etc
        if ticket.is_public:
            pfile.make_public() # the tag and related files have to have the same visibility as the ticket
        pfile.allow_staff()     # staff has to have r/w access to all imported tickets, and related files

        # add requester (ro)
        pfile.add_user(ticket.requester, write=False)

        # add volunteers (rw)
        for v in ticket.volunteers.all():
            pfile.add_user(v, write=True)
    else:
        pfile.allow_staff()


def handle_folder_id(service, ticket_id, folder_id):
    file_ids_list = list_folder_contents(service, folder_id)

    ### TICKET
    # first, we need the ticket
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        print '     +-- missing ticket: %s' % ticket_id
        return

    print '     +-- ticket : %s' % ticket_id
    print '     +-- file   : %s' % f['localPath']

    # get file metadata
    file_info_list = []
    for f in file_ids_list:
        f = get_file_metadata(service, f['id'])
        if f['id'] not in imported_files:
            print '     +-- %s: not in imported files, file will be downloaded' % f['id']
            file_info_list.append(f)
        elif f['md5Checksum'] != imported_files[f['id']]['md5Checksum']:
            print '     +-- %s: md5Checksum (%s vs. %s) mismatch, file will be downloaded' % (f['id'], f['md5Checksum'], imported_files[f['id']]['md5Checksum'])
            file_info_list.append(f)
        else:
            print '     +-- %s: file already imported, md5Checksum matches; not downloading' % f['id']

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
        f['localPath'] = os.path.join(dfolder, f['originalFilename'])
        f['legacyGoogleFolderId'] = folder_id

        # download/checksum the file
        handle_gdrive_file(service, f)

        # handle the podaci side of things
        podacify_file(imported_files, f, ticket=ticket)

        # remove the file?
        if not keep_downloads:
            os.remove(f['localPath'])

    # remove the folder?
    if not keep_downloads:
        os.rmdir(dfolder)



if __name__ == "__main__":

    keep_downloads = True
    try:
        # requried args
        script, idpath, drivefolderids_path = sys.argv[:3]
        # --keep?
        if len(sys.argv) > 3:
            if sys.argv[3] == '--keep':
                keep_downloads = True
            else:
                raise ValueError
            # too long, did not read
            if len(sys.argv) > 4:
                raise ValueError
    except ValueError:
        print("\nRun via:\n\t%s </path/to/legacy-investigative-dashboard> <drive-folder-ids-file-path> [--keep]\n" % sys.argv[0])
        print("Temporary files are being saved in:\n\t/tmp/id_gdrive_downloads/<folder-id>/<individual-filenames>\n\nOptional --keep parameter makes the script not delete the downloaded temporary files after Podaci import.\nFiles on GDrive are not automatically deleted under any circumstances.\n")
        sys.exit()

    # imported files ids pickled dump file
    imported_files_file = os.path.join(
        os.path.dirname(
          os.path.abspath(
            drivefolderids_path
          )
        ), 'GDrive.importedfiles')


    # the "d" is silent
    print "Setting up django..."
    django.setup()

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

    # files already imported
    print "Loading imported files data..."
    try:
        with open(imported_files_file, 'rb') as iffile:
            imported_files = pickle.load(iffile)
        print '+-- loaded %d imported file data from %s' % (len(imported_files), imported_files_file)
    except:
        print "+-- warning, no imported file data loaded, tried from %s." % imported_files_file


    # podaci tickets meta tag
    # metatag, created = Tag.objects.get_or_create(name='Tickets_Meta_Tag')
    # metatag.allow_staff()

    # create the damn gdrive service
    service = create_system_service()


    # handling the keyboard interrupt gracefully
    try:
        # get folder contents
        for ticket_id in drivefolderids:
            # let's handle a google drive folder, shall we?
            handle_folder_id(service, ticket_id, drivefolderids[ticket_id])
        # should we tidy things up?
        if not keep_downloads:
            # remove id_gdrive_downloads folder
            os.rmdir('/tmp/id_gdrive_downloads/')
    except KeyboardInterrupt:
        print 'KeyboardInterrupt caught, exiting gracefully'
    #except Exception as e:
    #   print 'Exception caught: %s (%s); exiting gracefully' % (e, type(e))


    # have we actually saved any files?
    if imported_files:
        try:
            with open(imported_files_file, 'wb') as iffile:
                pickle.dump(imported_files, iffile)
            print "Dumped %d drive folder ids to %s." % (len(imported_files), imported_files_file)
        except:
            print 'Dumping %d drive folder ids %s has failed!..' % (len(imported_files), imported_files_file)
