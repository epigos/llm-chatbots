# Gunicorn configuration file
import multiprocessing

workers = multiprocessing.cpu_count() * 2
print("Number of cpu workers:", workers)

bind = "0.0.0.0:8000"

loglevel = "info"
errorlog = "-"
accesslog = "-"
timeout = 120
graceful_timeout = 120
keepalive = 65
chdir = "/code/"
worker_class = "uvicorn.workers.UvicornWorker"
forwarded_allow_ips = "*"
