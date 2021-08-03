import logging
from os import mkdir

LOGS_DIR = "./logs/"

try:
    mkdir(LOGS_DIR)
except OSError:
    print("Directory exists.")
else:
    print("Created the logs directory.")

LOG_CONFIG = dict(
    version=1,
    formatters={
        "simple": {
            "format": "[%(asctime)s] [%(levelname)s] - : %(message)s.",
            "datefmt": "%H:%M:%S",
        },
        "detailed": {
            "format": "[%(asctime)s] [%(levelname)s] - Line: %(lineno)d "
            "- %(name)s - : %(message)s.",
            "datefmt": "%d/%m/%y - %H:%M:%S",
        },
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": logging.INFO,
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "level": logging.INFO,
            "filename": LOGS_DIR + "logfile.log",
        },
    },
    root={
        "level": logging.INFO,
        "handlers": [
            "file",
        ],
    },
)
