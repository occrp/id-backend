import sys
import httplib2
import logging

from apiclient import errors
from apiclient.discovery import build
from oauth2client import client
from app.i18n import lazy_gettext as _

from app.config import config


class GroupsError(Exception):
    pass


def http_error(e):
    logging.exception(e.message)
    raise GroupsError(_('Error connecting to Google Groups.'))


def api_call(acceptable_error_codes=None):
    """
    Simple exception handling for functions that make api calls to google.
    Has a blithe disregard for api exception details, but covers our butts.
    """

    success_codes = [] if not acceptable_error_codes else acceptable_error_codes

    def decorator(f):
        def fn(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except errors.HttpError as e:
                if not int(e.resp['status']) in success_codes:
                    http_error(e)
        return fn
    return decorator


class Groups(object):

    def __init__(self):
        self.service = self._create_groups_client()

    def _create_groups_client(self):
        credentials = client.SignedJwtAssertionCredentials(
            config['drive_service_account'],
            config['drive_private_key'],
            scope=[
                'https://www.googleapis.com/auth/admin.directory.group',
                'https://www.googleapis.com/auth/admin.directory.user.readonly'],
            prn=config['drive_owner_account']
        )

        http = httplib2.Http(cache=memcache)
        http = credentials.authorize(http)

        try:
            return build('admin', 'directory_v1', http=http)
        except NotImplementedError:
            raise GroupsError(_('Your private key must be in "PEM" format.'))
        except client.AccessTokenRefreshError:
            raise GroupsError(_('Error refreshing the access token. Check '
                                'your settings and try again.'))

    @classmethod
    def system_instance(cls):
        """
        Returns a cached instance of Groups initialized with the
        system account.
        """
        # Que?
        pass
        #app = webapp2.get_app()
        #groups = app.registry.get('groups')
        #if not groups:
        #    groups = cls()
        #    app.registry['groups'] = groups
        #eturn groups

    @api_call(acceptable_error_codes=[409])
    def add_to(self, group, email):
        (self.service.members()
            .insert(
                groupKey=group,
                body={'email': email})
            .execute())

    @api_call(acceptable_error_codes=[404])
    def remove_from(self, group, email):
        (self.service.members()
            .delete(groupKey=group, memberKey=email)
            .execute())

    @api_call(acceptable_error_codes=[])
    def get_members(self, group):
        members = []
        pageToken = None
        while True:
            result = self.service.members().list(groupKey=group,
                                                 pageToken = pageToken,
                                                 maxResults=99999
                                           ).execute()
            members += result['members']
            pageToken = result.get('nextPageToken', None)
            if pageToken is None:
                 break
        return members
