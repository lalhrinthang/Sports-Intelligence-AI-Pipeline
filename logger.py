import logging
from datetime import datetime # for timestamping log entries
import sys
import io

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Set the logging level to INFO
    format='%(asctime)s | %(levelname)s | %(message)s', # Log format includes timestamp, log level, and message
    handlers=[
        logging.FileHandler('logfile.txt', encoding='utf-8'), # Log to file with UTF-8 encoding
        logging.StreamHandler() # Also log to the console
    ]
)

logger = logging.getLogger('SyndicatePipeline') # Create a logger for the syndicate pipeline

def log_step(step_name,status,details=""):
    """
    Logs the execution of a step in the pipeline.
    
    Parameters:
    - step_name: Name of the step being logged
    - status: Status of the step (e.g., 'STARTED', 'COMPLETED', 'FAILED')
    - details: Additional details about the step
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Get current timestamp
    
    if status == 'FAILED':
        logger.error(message) # Log the message at ERROR level if the step failed
    elif status == 'SUCCESS':
        logger.info(message) # Log the message at INFO level if the step completed successfully 
    else:
        logger.info(message) # Log the message at INFO level for other statuses (e.g., STARTED)