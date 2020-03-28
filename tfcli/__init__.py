import logging
import colorlog

__version__ = "0.0.1"


def format_logger(logger: logging.Logger, debug: bool):
    message_format = "%(log_color)s[%(asctime)s.%(msecs).03d pid#%(process)d# %(levelname).1s] %(message)s"
    date_format = "%Y%m%dT%H:%M:%S"
    log_colors = {"DEBUG": "cyan",
                  "INFO": "green",
                  "WARNING": "yellow",
                  "ERROR": "red",
                  "CRITICAL": "white,bg_red"
                  }
    format = colorlog.ColoredFormatter(
        message_format, datefmt=date_format, log_colors=log_colors)

    loggingStreamHandler = logging.StreamHandler()
    loggingStreamHandler.setFormatter(format)
    logger.addHandler(loggingStreamHandler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
