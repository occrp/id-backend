from django.conf import settings
from pq.tasks import PQ
from psycopg2.errors import DuplicateTable
from psycopg2.pool import ThreadedConnectionPool


pool = ThreadedConnectionPool(1, 5, settings.QUEUE_DATABASE_URL)
pq = PQ(pool=pool)

try:
    pq.create()
except DuplicateTable:
    pass

queue = pq[settings.QUEUE_NAME]
