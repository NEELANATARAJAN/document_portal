import os
import logging
from datetime import datetime

class CustomLogger:
    def __init__(self):
        """
            init method of Custom Logger class creates log folder and 
            logfile (based on current timestamp) along with basic configuration
        """
        self.log_path=os.path.join(os.getcwd(),"logs")
        os.makedirs(self.log_path,exist_ok=True)

        log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path=os.path.join(self.log_path,log_file)

        

    def get_logger(self,name=__file__):
        """
            get_logger modeule will return the file name of the class that raises logs
        """
        logger_name = os.path.basename(name)

        # Configure logging for file + console
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            # handlers=[file_handler]
            handlers=[console_handler, file_handler]
        )
        return logging.getLogger(os.path.basename(name))


if __name__=="__main__":
    logger=CustomLogger()
    logger=logger.get_logger(__file__)
    logger.info("Custom Logger initialized...")
    logger.info("Moving on to exception handling...")
