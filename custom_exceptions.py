"""
Developer Info
--------------
Developed By: Nicholas Gambirasi
Created On: 02 October 2023
Last Edited: 02 October 2023

Purpose
--------------
This file defines several exceptions that are raised
during the execution of `run.py`
"""
class ActionArgumentsException(BaseException):

    """
    Raised when there are issues with the action arguments
    provided in the command line tool
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)

class UnsupportedFileTypeError(BaseException):

    """
    Raised when an unsupported file type is specified when
    saving the processed csv files
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)

class UnsupportedPlotError(BaseException):

    """
    Raised when an unsupported plot argument is declared
    when calling the `plotting.plot_data` function
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)

class NanException(BaseException):

    """
    Raised when processing of the data in preparation
    for plotting generates NaN values in the new
    columns
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)
