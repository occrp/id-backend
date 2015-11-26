import logging
from settings.settings import AUTH_USER_MODEL
from id.models import Profile
from core.models import AuditLog
#logger = logging.getLogger(__name__)

class AuditLogHandler(logging.Handler):
    """An log handler that stores log entries in the AuditLog database.
    """

    def emit(self, record):
        log = AuditLog()
        log.level = record.levelno
        log.module = record.module
        log.process = record.process
        log.thread = record.thread
        log.message = record.message
        log.filename = record.filename
        log.lineno = record.lineno
        log.funcname = record.funcName
        log.exctext = record.exc_text
        log.excinfo = record.exc_info
        if hasattr(record, 'request'):
            log.ip = record.request.META.get('REMOTE_ADDR', None)
            if record.request.is_authenticated():
                log.user = record.request.user
        elif hasattr(record, 'user'):
            log.user = record.user

        log.save()
