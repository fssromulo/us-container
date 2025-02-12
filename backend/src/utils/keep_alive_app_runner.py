# Python imports
import time

# Pip imports
import requests
from loguru import logger


def keep_alive():
    """Send a GET request to keep the server alive."""
    # print timing of request

    start_time = time.time()
    # requests.get('https://ivpgm5nsxn.us-west-2.awsapprunner.com/', timeout=30)
    requests.get('https://api.mobilestoragetech.com//', timeout=30)
    # print average time between requests
    logger.info(f"Average time between requests: {time.time() - start_time}")


if __name__ == '__main__':
    while True:
        keep_alive()
        time.sleep(5)  # Sleep for 60 seconds before making the next request
