command = '/home/techops/nwapp-back/env/bin/gunicorn'
pythonpath = '/home/techops/nwapp-back/nwapp'
bind = '127.0.0.1:8001'
workers = 3
timeout = 600
graceful_timeout = 60
