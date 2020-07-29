import logging
import configuration

logging.root.handlers = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(configuration.SYSTEM_SETTINGS['LOG_FILE_LOCATION']),
        logging.StreamHandler()
    ]
)