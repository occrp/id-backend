import httplib2
import logging

# import webapp2
# from google.appengine.api import memcache
from apiclient import errors
from apiclient.discovery import build
from apiclient.http import BatchHttpRequest, MediaIoBaseUpload
from oauth2client import client
#from oauth2client.appengine import OAuth2Decorator
from django.utils.translation import ugettext_lazy as _

import settings
# from app.utils import key_to_json


# drive_decorator = OAuth2Decorator(
#    client_id=config['app_oauth_consumer_key'],
#    client_secret=config['app_oauth_consumer_secret'],
#    scope='https://www.googleapis.com/auth/drive'
#)


def http_error(e):
    """
    Logging exception handler for Drive HTTP errors.
    """
    logging.exception(e.message)
    raise DriveError(_('Error connecting to Google Drive.'))


def create_callback(responses=None):
    """
    Creates a callback that gets passed to the BatchHttpRequest constructor.
    Enables the callback to append to a list of responses.
    """
    def callback(request_id, response, exception):
        if exception:
            http_error(exception)
        if type(responses) is list:
            responses.append(response)
    return callback


def batchable(func):
    """
    Decorator for marking methods that can be batched together using
    BatchHttpRequest.
    """
    def wrapper(self, *args, **kwargs):
        # Short-circuit calls with empty lists of file_ids
        if not args[0]:
            return

        # Create a new batch if one wasn't provided
        local_batch = None
        responses = []
        if 'batch' not in kwargs:
            local_batch = BatchHttpRequest(callback=create_callback(responses))
            kwargs['batch'] = local_batch

        # Call the wrapped method
        func(self, *args, **kwargs)

        # If a batch wasn't provided, execute the local batch
        if local_batch:
            local_batch.execute()
            return responses
        return None
    return wrapper


class DriveError(Exception):
    pass


class Drive(object):

    def __init__(self, http=None):
        if http:
            self.service = self._create_user_service(http)
        else:
            self.service = self._create_system_service()

    def _create_user_service(self, http):
        """
        Builds and returns a Drive service object authorized with a user's
        httplib2.Http instance.
        """
        try:
            return build('drive', 'v2', http=http)
        except client.AccessTokenRefreshError:
            raise DriveError(_('Error refreshing Google Drive access token.'))

    def _create_system_service(self):
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

        http = httplib2.Http(cache=memcache)
        http = credentials.authorize(http)

        try:
            return build('drive', 'v2', http=http)
        except NotImplementedError:
            raise DriveError(_('Your Google Drive private key must be in '
                               '"PEM" format.'))
        except client.AccessTokenRefreshError:
            raise DriveError(_('Error refreshing Google Drive access token. '
                               'Check your settings and try again.'))

    def about(self):
        try:
            return self.service.about().get().execute()
        except errors.HttpError as e:
            http_error(e)

    def create_folder(self, title, parent_id):
        logging.info('Creating folder with title "%s"' % title)
        body = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_id}]
        }
        try:
            return self.service.files().insert(body=body).execute()['id']
        except errors.HttpError as e:
            http_error(e)

    def ensure_folder(self, title,
                      parent_id=config['drive_grouped_folder_id']):
        """
        Ensures a directory exists with the given title. If one does not exist,
        it's created.
        """
        logging.info('Checking if folder exists with title "%s" under parent '
                     'ID %s.' % (title, parent_id))
        items = None
        query = ("'%s' in owners and "
                 "trashed=false and "
                 "mimeType='application/vnd.google-apps.folder' and "
                 "title='%s'" % (config['drive_owner_account'], title))
        try:
            items = self.service.children().list(
                q=query, folderId=parent_id).execute()['items']
        except errors.HttpError as e:
            http_error(e)

        if items:
            return items[0]['id']
        return self.create_folder(title, parent_id)

    def get_owner_account_role(self, file_ids):
        """
        Takes a list of file IDs and returns a list of files with the ACL role
        of the Drive owner account for each one.
        """
        logging.info('Getting ACLs for file IDs %s.' % file_ids)
        acls = []

        def callback(request_id, response, exception):
            if exception:
                http_error(exception)
            for p in response['items']:
                if p['id'] == config['drive_owner_permission_id']:
                    return acls.append((request_id, p['role']))
            return acls.append((request_id, None))

        batch = BatchHttpRequest(callback=callback)
        for file_id in file_ids:
            batch.add(self.service.permissions().list(fileId=file_id),
                      request_id=file_id)
        batch.execute()

        return acls

    def upload(self, file_ids, obj):
        """
        Kicks off the process of uploading a doc to Investigative Dashboard
        """
        # Clearly name the instances of Drive we're using
        user_drive = self
        owner_drive = Drive.system_instance()

        # Make sure there is a folder for the given object in Drive
        if not obj.drive_folder_id:
            title = key_to_json(obj.key)
            parent_id = config['drive_grouped_folder_id']
            obj.drive_folder_id = owner_drive.ensure_folder(title, parent_id)
            obj.put()
        folder_id = obj.drive_folder_id

        # Determine which files being uploaded are new to the system or
        # are already owned by the system account.
        existing = []
        new = []
        for file_id, role in user_drive.get_owner_account_role(file_ids):
            if role == 'owner':
                existing.append(file_id)
            else:
                new.append(file_id)

        # Share new files with owner account
        user_drive.share(new, [config['drive_owner_account']], 'user', 'reader')

        # Copy new files using owner account
        batch = BatchHttpRequest(callback=create_callback())
        owner_drive.copy_to_folders(new, [folder_id], batch=batch)

        # Move existing, owned files into correct folder
        owner_drive.add_parent(existing, folder_id, batch=batch)
        batch.execute()

    def _upload_file(self, fh, folder_id, title, mimetype="application/pdf"):
        # relevant doc: https://developers.google.com/drive/v2/reference/files/insert#examples
        # Clearly name the instances of Drive we're using
        owner_drive = Drive.system_instance()

        media_body = MediaIoBaseUpload(fh, mimetype=mimetype, resumable=True)
        body = {'title': title,
                'description': '',
                'mimeType': mimetype,
                'parents': [{'id': folder_id}]
               }
        try:
            file = owner_drive.service.files().insert(
                body=body,
                media_body=media_body).execute()
            return file
        except errors.HttpError, error:
            print 'error: %s' % error
            return

    def get_ids(self, responses):
        if responses:
            return [r['id'] for r in responses]
        return []

    @batchable
    def copy_to_folders(self, file_ids, folder_ids, batch=None):
        """
        Makes copies of a given set of files and transfers them to a given
        folder.
        """
        logging.info('Copying file IDs %s to folder IDs %s.' % (file_ids,
                                                                folder_ids))
        body = {'parents': [{'id': id} for id in folder_ids]}
        for file_id in file_ids:
            batch.add(self.service.files().copy(fileId=file_id, body=body))

    @batchable
    def trash(self, file_ids, batch=None):
        """
        Takes a list of file IDs moves them to the user's trash.
        """
        logging.info('Trashing file IDs %s.' % file_ids)
        for file_id in file_ids:
            batch.add(self.service.files().trash(fileId=file_id))

    @batchable
    def add_parent(self, file_ids, folder_id, batch=None):
        """
        Adds a parent to a given set files.
        """
        logging.info('Adding parent %s to file IDs %s.' % (folder_id, file_ids))
        parent = {'id': folder_id}
        for file_id in file_ids:
            batch.add(self.service.parents().insert(fileId=file_id,
                                                    body=parent))

    def share(self, file_ids, values, type, role):
        """
        Takes a list of file IDs and shares them with a list of users.

        Google seems to fail on batching permission changes.
        Hence no batching.
        See the following issue:
        https://code.google.com/p/google-api-python-client/issues/detail?id=260
        """
        logging.info('Adding %s as a %s on file IDs %s.' % (values, role,
                                                            file_ids))
        for file_id in file_ids:
            for value in values:
                perm = {
                    'value': value,
                    'type': type,
                    'role': role,
                }
                try:
                    self.service.permissions().insert(
                        fileId=file_id,
                        body=perm,
                        sendNotificationEmails=False).execute()
                except errors.HttpError as e:
                    http_error(e)

    @batchable
    def remove_from_folder(self, file_ids, folder_id, batch=None):
        """
        Removes a given set of files from a folder.
        """
        logging.info('Removing file IDs %s from folder %s.' %
                     (file_ids, folder_id))
        for file_id in file_ids:
            batch.add(self.service.parents().delete(fileId=file_id,
                                                    parentId=folder_id))

    def list_files(self, folder_id=None):
        """
        Returns a list of the files that the document owner account owns.
        """
        q = ("'%s' in owners and trashed=false"
             % config['drive_owner_account'])
        if folder_id:
            q += " and '%s' in parents" % folder_id
        try:
            return self.service.files().list(q=q).execute()['items']
        except errors.HttpError as e:
            http_error(e)

    def search(self, query):
        """
        Queries all the documents in Google Drive
        """
        query = query.replace("\\", "\\\\").replace("'", "\\'")
        q = "'%s' in owners" % config['drive_owner_account']
        q += " and fullText contains '%s'" % query
        q += " and mimeType != 'application/vnd.google-apps.folder'"
        try:
            return self.service.files().list(q=q).execute()['items']
        except errors.HttpError as e:
            http_error(e)

    def clear_permissions(self, file_id):
        """
        Deletes all the permissions for a given set of files.
        """
        try:
            perms = (self.service.permissions()
                     .list(fileId=file_id).execute()['items'])
        except errors.HttpError as e:
            http_error(e)

        for p in perms:
            if p['role'] != 'owner':
                self.service.permissions().delete(fileId=file_id,
                                                  permissionId=p[
                                                      'id']).execute()

    @classmethod
    def system_instance(cls):
        """
        Returns a cached instance of Drive initialized with the
        system account. Do not use this when you want transfer ownership
        of a file or otherwise impersonate a user other than the
        system account.
        """
        pass
        #try:
        #    app = webapp2.get_app()
        #    drive = app.registry.get('drive')
        #    if not drive:
        #        drive = cls()
        #        app.registry['drive'] = drive
        #except AssertionError: # happens when we aren't running under WSGI
        #    drive = cls()
        #return drive
