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
    
    message = f"{timestamp} | [{step_name}] | Status: {status} | {details}" # Format log message
    if status == 'FAILED':
        logger.error(message) # Log the message at ERROR level if the step failed
    elif status == 'SUCCESS':
        logger.info(message) # Log the message at INFO level if the step completed successfully 
    else:
        logger.info(message) # Log the message at INFO level for other statuses (e.g., STARTED)