"""
This module defines the logging parameters for the program.
"""

import logging
import configuration

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logging.root.handlers = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(configuration.SYSTEM_SETTINGS['LOG_FILE_LOCATION']),
        logging.StreamHandler()
    ]
)