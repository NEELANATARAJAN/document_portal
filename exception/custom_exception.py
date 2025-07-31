import os
import sys
import traceback
from logger.custom_logger import CustomLogger

# Custom Logger object is created to store any exception on to a log file

logger=CustomLogger().get_logger(__file__)

class DocumentPortalException(Exception):
    def __init__(self, error_message, error_details:sys):
        """
            init method initializes exception info, file name, line number, error message and 
            full traceback details
        """
        _,_,exc_tb=error_details.exc_info()
        self.file_name=exc_tb.tb_frame.f_code.co_filename
        self.line_no=exc_tb.tb_lineno
        self.error_message=str(error_message)
        self.traceback_string=''.join(traceback.format_exception(*error_details.exc_info()))

    def __str__(self):
        """
            str dunder method formats the exception in readable format
        """
        print(f"""
        Error in [{self.file_name}] at line [{self.line_no}]
        Message: {self.error_message}
        Traceback:
        {self.traceback_string}
        """)
        return f"""
        Error in [{self.file_name}] at line [{self.line_no}]
        Message: {self.error_message}
        Traceback:
        {self.traceback_string}
        """ 

if __name__=="__main__":
    try:
        a=1/0
        print(a)
    except Exception as e:
        app_exc=DocumentPortalException(e, sys)
        print(f"app_exc:\n\n{app_exc}\n\n")
        logger.exception(app_exc)
        # raise app_exc
