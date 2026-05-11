"""日志模块"""
import logging, os, traceback
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / f'app_{datetime.now():%Y%m%d}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('shuzhi')


def log_error(msg):
    logger.error(msg)
    logger.debug(traceback.format_exc())


def log_info(msg):
    logger.info(msg)


def log_warn(msg):
    logger.warning(msg)
