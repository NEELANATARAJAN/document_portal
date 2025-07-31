import os
import sys
import logging
import structlog
from datetime import datetime

class CustomLogger:
    def __init__(self,logs_dir='logs'):
        """
            init method of Custom Logger class creates log folder and 
            logfile (based on current timestamp) along with basic configuration
        """
        self.log_path=os.path.join(os.getcwd(),logs_dir)
        os.makedirs(self.log_path,exist_ok=True)
        
        log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path=os.path.join(self.log_path,log_file)
        

    def get_logger(self,name):
        """
            get_logger modeule will return the file name of the class that raises logs
        """
        logger_name = os.path.basename(name)
        print(f"\n\nbasename: {logger_name}\n\n")

        # Configure logging for file + console
        file_handler = logging.FileHandler(self.log_file_path)
        print(f"\n\nname={name},\nfile:{self.log_file_path}\n\n")
        file_handler.setLevel(logging.INFO)
        # formatter=structlog.stdlib.ProcessorFormatter(
        #     processor=structlog.dev.ConsoleRenderer(),
        #     foreign_pre_chain=[
        #         structlog.stdlib.add_logger_name,
        #         structlog.stdlib.add_log_level,
        #     ]
        # )
        # file_handler.setFormatter(logging.Formatter("%(message)s"))
        file_handler.setFormatter(structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
            ]
        ))

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
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True
        )

        return structlog.get_logger(logger_name)


if __name__=="__main__":
    logger=CustomLogger().get_logger(__file__)
    print(f"fileinmain:{__file__}\n\n")
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
