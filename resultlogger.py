import logging
import json
import os
from datetime import datetime

class TLSLogger():
    def __init__(self, run_name, tls_ids, data_types,
            to_file=False, to_console=False, directory=None, is_timestamped=False, fmt="log"):
        self.run_name = run_name
        self.tls_ids = tls_ids
        self.data_types = data_types
        self.directory = directory
        self.is_timestamed = is_timestamped
        self.fmt = fmt
        self.to_file = to_file
        self.to_console = to_console
        
        self.logger = None
        if self.to_file and self.directory:
            self.logger = get_logger(
                self.run_name, directory, is_timestamped, fmt)

    def build_output_dict(self, data_dict):
        """
        Check that requested content key exists and provided data is not empty
        """
        build_dict = {}
        for k, v in data_dict.items():
            if k in self.data_types and v:
                build_dict.update({k: v})
        return build_dict

    def log(self, time, data_dict):
        """
        Log int file
        """
        output_dict = {"time": time}
        output_data_dict = self.build_output_dict(data_dict)
        output_dict.update(output_data_dict)

        if self.to_file and self.logger:
            self.logger.info('%s', output_dict)
        if self.to_console:
            print(f"{output_dict}")

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