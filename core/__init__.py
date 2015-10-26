import logging

logger = logging.getLogger('django.db.backends.schema')
logger.setLevel(logging.INFO)

logger = logging.getLogger('django_select2')
logger.setLevel(logging.INFO)

logger = logging.getLogger('urllib3.connectionpool')
logger.setLevel(logging.WARN)

logger = logging.getLogger('pycountry.db')
logger.setLevel(logging.WARN)
