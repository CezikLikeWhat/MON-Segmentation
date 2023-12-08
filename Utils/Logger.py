import logging
import sys

ANSI_MAGENTA = '\033[35;49;1m'
ANSI_RED = '\033[31;40;1m'
ANSI_RESET = '\033[0m'
ANSI_YELLOW = '\033[33;40;1m'
ANSI_GREEN_UNDERLINE = '\033[32;49;4;1m'


class Logger:
    @staticmethod
    def info(message):
        logger = logging.getLogger('info_logger')
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.setLevel(logging.INFO)
        info_handler = logging.StreamHandler(sys.stdout)
        info_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            f'{ANSI_GREEN_UNDERLINE}LOGGER{ANSI_RESET}({ANSI_MAGENTA}%(asctime)s{ANSI_RESET}) | {ANSI_YELLOW}%(levelname)s{ANSI_RESET} - %(message)s')
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)
        logger.info(message)

    @staticmethod
    def error(message):
        logger = logging.getLogger('error_logger')
        if logger.hasHandlers():
            logger.handlers.clear()
        logger.setLevel(logging.ERROR)
        error_handler = logging.StreamHandler(sys.stdout)
        error_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            f'{ANSI_GREEN_UNDERLINE}LOGGER{ANSI_RESET}({ANSI_MAGENTA}%(asctime)s{ANSI_RESET}) | {ANSI_RED}%(levelname)s{ANSI_RESET} - %(message)s')
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        logger.error(message)
