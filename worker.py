"""
RQ Worker Entry Point
---------------------
Starts a Redis Queue worker that listens on the 'default' queue.
Run this in the worker container: python worker.py
"""

import os
import logging
from redis import Redis
from rq import Worker, Queue

# Eagerly import all models so SQLAlchemy's mapper can resolve string references
import app.models.course    # noqa
import app.models.lesson    # noqa
import app.models.question  # noqa
import app.models.option    # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if __name__ == "__main__":
    logger.info(f"Connecting to Redis at: {REDIS_URL}")

    conn = Redis.from_url(REDIS_URL)
    queues = [Queue("default", connection=conn)]

    logger.info("RQ Worker started. Listening on 'default' queue...")

    # Start the worker — it will process jobs from app/workers/tasks.py
    worker = Worker(queues, connection=conn)
    worker.work()
