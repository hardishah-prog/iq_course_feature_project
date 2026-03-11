"""
redis_conn.py
-------------
Creates a shared Redis connection and RQ queue instance.

Usage:
    from app.redis_conn import redis_conn, task_queue
"""

import os
from redis import Redis
from rq import Queue

# Load REDIS_URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Shared Redis connection
redis_conn = Redis.from_url(REDIS_URL)

# Default RQ queue — background jobs are enqueued here
task_queue = Queue("default", connection=redis_conn)
