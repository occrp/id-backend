from django.conf import settings
from pq.tasks import PQ
from psycopg2.errors import UndefinedTable
from psycopg2.pool import ThreadedConnectionPool


pool = ThreadedConnectionPool(1, 5, settings.QUEUE_DATABASE_URL)
pq = PQ(pool=pool)
queue = pq[settings.QUEUE_NAME]
# TODO: Look into this weird side-effect...
queue.timeout = float(queue.timeout)

try:
    len(queue)
except UndefinedTable:
    pq.create()
