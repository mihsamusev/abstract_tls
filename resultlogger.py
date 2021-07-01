import logging
import json
import os
from datetime import datetime

def get_logger(run_name, directory=None, is_timestamped=False, fmt="log"):
    """
    Logger for results
    """
    
    if directory is None:
        directory = os.getcwd()
    else:
        os.makedirs(directory, exist_ok=True)

    name_id = ""
    if is_timestamped:
        name_id = "_" + datetime.now().strftime('%Y%m%d%H%M%S')
    
    run_id = run_name + name_id + "." + fmt
    path = os.path.join(directory, run_id)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(message)s")
    
    if len(logger.handlers) == 0:
        file_handler = logging.FileHandler(path, "w")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    pass