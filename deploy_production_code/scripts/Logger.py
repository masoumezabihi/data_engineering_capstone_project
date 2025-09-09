import os
import logging

class Logger:
    @staticmethod
    def setup_logger(app_name='open_fda_etl', log_folder='log', log_filename='open_fda_etl.log', log_level=logging.INFO):
        """
        Sets up logging configuration.
        Logs to file in local, logs to console only in Databricks.
        """
        handlers = []

        # Detect if running on Databricks
        is_databricks = 'DATABRICKS_RUNTIME_VERSION' in os.environ

        if not is_databricks:
            # Local: log to file + console
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)
            log_path = os.path.join(log_folder, log_filename)
            handlers.append(logging.FileHandler(log_path, mode='w'))

        # Console output always included
        handlers.append(logging.StreamHandler())

        logging.basicConfig(
            level=log_level,
            format=f'%(asctime)s - {app_name} - %(levelname)s - %(message)s',
            handlers=handlers
        )

    @staticmethod
    def log(message, level=logging.INFO):
        """
        Logs a message.
        """
        if isinstance(level, str):
            level = level.lower()
            log_func = getattr(logging, level, None)
            if not callable(log_func):
                logging.warning(f"[Logger] Invalid log level: {level}. Defaulting to WARNING.")
                log_func = logging.warning
        else:
            level_name = logging.getLevelName(level).lower()
            log_func = getattr(logging, level_name, logging.warning)

        log_func(message)
