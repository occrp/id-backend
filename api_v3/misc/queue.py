from django.db import connections
from django.conf import settings
from pq.tasks import PQ
from psycopg2.errors import DuplicateTable
from psycopg2.pool import ThreadedConnectionPool


connections['default'].connect()
pool = ThreadedConnectionPool(1, 5, connections['default'].connection.dsn)
connections['default'].close()
pq = PQ(pool=pool)

try:
    pq.create()
except DuplicateTable:
    pass

queue = pq[settings.QUEUE_NAME]
