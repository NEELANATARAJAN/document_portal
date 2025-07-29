import os
import logging
from datetime import datetime

class CustomLogger:
    def __init__(self):
        """
            init method of Custom Logger class creates log folder and 
            logfile (based on current timestamp) along with basic configuration
        """
        log_path=os.path.join(os.getcwd(),"logs")
        os.makedirs(log_path,exist_ok=True)

        log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        log_file_path=os.path.join(log_path,log_file)

        logging.basicConfig(
            filename=log_file_path,
            format="[ %(asctime)s] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s",
            level=logging.INFO
        )

    def get_logger(self,name=__file__):
        """
            get_logger modeule will return the file name of the class that raises logs
        """
        print(name)
        return logging.getLogger(os.path.basename(name))


if __name__=="__main__":
    logger=CustomLogger()
    logger=logger.get_logger(__file__)
    logger.info("Custom Logger initialized...")
    logger.info("Moving on to exception handling...")
