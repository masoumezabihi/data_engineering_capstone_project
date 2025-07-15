import os
import logging

class Logger:
    @staticmethod
    def setup_logger(log_folder='log', log_filename='data_pipeline.log', log_level=logging.DEBUG):
        """
        Sets up logging configuration for the application.
        
        Parameters:
            log_folder (str): The folder to store log files.
            log_filename (str): The name of the log file.
            log_level (int): The log level (default: DEBUG).
            
        Returns:
            logging.Logger: The configured logger instance.
        """
        # Ensure the log folder exists
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Full path for the log file
        log_file = os.path.join(log_folder, log_filename)

        # Set up the logging configuration
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, mode='w')]
        )

    @staticmethod
    def log(message="", level=logging.DEBUG):
        """
        Static method to log a message at the given level.

        Parameters:
            level (int): The logging level (default: DEBUG).
            message (str): The message to log.
        """
        # Ensure the level is one of the valid logging levels
        if isinstance(level, str):
            level = level.lower()
            log_func = getattr(logging, level, None)
            if log_func is None:
                logging.warning(f"Invalid log level: {level}. Logging message as WARNING: {message}")
                log_func = logging.warning
        else:
            log_func = logging.getLevelName(level).lower()
            log_func = getattr(logging, log_func, logging.warning)

        log_func(message)
