import logging
from config import config

log_config = config['logging']

logging.basicConfig(
    level=getattr(logging, log_config['level']),
    format=log_config['format']
)

def get_logger(name):
    return logging.getLogger(name)
