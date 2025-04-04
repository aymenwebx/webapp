# gunicorn_conf.py
import multiprocessing

# Server socket
bind = '127.0.0.1:8000'  # Running on localhost port 8000

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'  # You can use 'gthread' or 'gevent' for async
threads = 4  # Only used with gthread worker class

# Timeouts
timeout = 30  # Seconds
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'debug'

# Process naming
proc_name = 'educa'

# Security
limit_request_fields = 32000
limit_request_field_size = 0  # Unlimited