"""
This module defines the logging parameters for the application.
"""

import logging
import configuration

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

"""m
from systemd.journal import JournalHandler

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)
log.info("sent to journal")
"""

logging.root.handlers = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(configuration.SYSTEM_SETTINGS['LOG_FILE_LOCATION']),
        logging.StreamHandler()
    ]
)
