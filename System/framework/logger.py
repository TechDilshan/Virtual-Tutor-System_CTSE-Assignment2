import logging

class Logger:
    def __init__(self):
        # Setting up basic logging configuration
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        self.logger = logging.getLogger()

    def log(self, message):
        """
        Log the provided message.
        """
        self.logger.info(message)

    def error(self, message):
        """
        Log an error message.
        """
        self.logger.error(message)