import os
import logging

LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')
logging.basicConfig(
    level=LOG_LEVEL
)
logging.info('============================================================')
logging.info('Set a LOG_LEVEL environment variable to remove INFO messages')
logging.info('============================================================')
