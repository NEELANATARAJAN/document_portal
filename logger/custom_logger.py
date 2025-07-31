import os
import sys
import logging
import structlog
from datetime import datetime

class CustomLogger:
    def __init__(self,name:str):
        """
            init method of Custom Logger class creates log folder and 
            logfile (based on current timestamp) along with basic configuration
        """
        self.log_path=os.path.join(os.getcwd(),"logs")
        os.makedirs(self.log_path,exist_ok=True)
        self.name=name

        log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path=os.path.join(self.log_path,log_file)

        self.std_logger=logging.getLogger(self.name)

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True
        )
        

    def get_logger(self,name):
        """
            get_logger modeule will return the file name of the class that raises logs
        """
        logger_name = os.path.basename(name)

        # Configure logging for file + console
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        formatter=structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_pre_chain=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
            ]
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            # handlers=[file_handler]
            handlers=[console_handler, file_handler]
        )
        # root_logger=logging.getLogger()
        # root_logger.addHandler(file_handler)
        # root_logger.setLevel(logging.INFO)
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True
        )

        return structlog.get_logger(logger_name)


if __name__=="__main__":
    logger=CustomLogger(__file__)
    logger=logging.getLogger(__file__)
    print(__file__)
    logger.debug("This is a debug message.", user_id="123", feature="login")
    logger.info("Custom Logger initialized...")
    logger.info("Moving on to exception handling...")
    # logger.warning("Disk space is low.", free_space_gb=5)
    # logger.error("Failed to connect to database.", db_host="localhost", port=5432)
    # logger.critical("System is shutting down due to critical error.")
    # try:
    #     1/0
    # except ZeroDivisionError as e:
    #     logger.exception("An unexpected error occured during execution...")
    
    # print(f"\nLog messages written to {__file__}...")
