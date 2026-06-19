"""Logging utilities for the BESS optimization project."""

import logging
import os
import sys


def setup_logging(log_level=logging.INFO, log_file=None, logger_name=None):
    """
    Set up logging configuration.

    Parameters
    ----------
    log_level : int, optional
        Logging level (e.g., logging.DEBUG, logging.INFO), by default logging.INFO
    log_file : str, optional
        Path to log file, by default None (logs to console only)
    logger_name : str, optional
        Name of the logger to configure, by default None (configures root logger)

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    # Create logs directory if logging to file
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Get logger
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()  # Root logger

    logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name, log_level=None):
    """
    Get a logger with the specified name.

    Parameters
    ----------
    name : str
        Name of the logger
    log_level : int, optional
        Logging level, by default None (uses parent logger's level)

    Returns
    -------
    logging.Logger
        Logger instance
    """
    logger = logging.getLogger(name)
    if log_level is not None:
        logger.setLevel(log_level)
    return logger
