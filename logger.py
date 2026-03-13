import logging
from datetime import datetime # for timestamping log entries

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Set the logging level to INFO
    format='%(asctime)s | %(levelname)s | %(message)s', # Log format includes timestamp, log level, and message
    handlers=[
        logging.FileHandler('logfile.txt'), # Log to a file named 'syndicate_pipeline.log'
        logging.StreamHandler() # Also log to the console
    ]
)
