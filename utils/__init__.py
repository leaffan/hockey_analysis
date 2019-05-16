#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import logging
import logging.handlers

from datetime import date


def retrieve_season(date_of_interest=None):
    """
    Identifies season based on month of given date, anything until June
    belongs to the season ending in the date's year, anything after
    June belongs to the season beginning in the date's year.
    NB: Season's are identified by the year they're beginning in, even for
    those that are shortened, i.e. 2012/13.
    """
    if date_of_interest is None:
        date_of_interest = date.today()
    if date_of_interest.month < 7:
        season = date_of_interest.year - 1
    else:
        season = date_of_interest.year

    return season


# utility class and functions for logging purposes
# logging formatter
class WhitespaceRemovingFormatter(logging.Formatter):
    """
    Defines a special logging formatter that removes '+ ' from the beginning
    of the logged message.
    """
    REGEX = re.compile(R"^\+?\s")

    def format(self, record):
        record.msg = record.msg.strip()
        record.msg = re.sub(self.REGEX, "", record.msg)
        return super(WhitespaceRemovingFormatter, self).format(record)


def prepare_logging(log_types=['file', 'screen'], logdir=''):
    """
    Prepares logging for the specified channels, e.g. 'file' (a log file) and
    'screen' (the command line).
    """
    logging.getLogger("requests").setLevel(logging.WARNING)

    if not logdir:
        logdir = os.path.join(os.getenv("TEMP"), "log")

    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    handlers = list()

    if 'screen' in log_types:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_formatter = logging.Formatter("%(message)s")
        stream_handler.setFormatter(stream_formatter)
        handlers.append(stream_handler)

    if 'file' in log_types:

        file_formatter = WhitespaceRemovingFormatter(
            "%(asctime)s.%(msecs)03d %(thread)5d " +
            "%(name)-35s %(levelname)-8s %(message)s",
            datefmt="%y-%m-%d %H:%M:%S")

        debug_log = os.path.join(logdir, 'pynhldb_debug.log')
        file_debug_handler = logging.handlers.TimedRotatingFileHandler(
            debug_log, when='midnight', interval=1)
        file_debug_handler.setFormatter(file_formatter)
        file_debug_handler.setLevel(logging.DEBUG)
        handlers.append(file_debug_handler)

        info_log = os.path.join(logdir, 'pynhldb_info.log')
        file_info_handler = logging.handlers.TimedRotatingFileHandler(
            info_log, when='midnight', interval=1)
        file_info_handler.setFormatter(file_formatter)
        file_info_handler.setLevel(logging.INFO)
        handlers.append(file_info_handler)

        warn_log = os.path.join(logdir, 'pynhldb_warn.log')
        file_warn_handler = logging.handlers.TimedRotatingFileHandler(
            warn_log, when='midnight', interval=1)
        file_warn_handler.setFormatter(file_formatter)
        file_warn_handler.setLevel(logging.WARN)
        handlers.append(file_warn_handler)

        logging.Formatter.formatTime

        error_log = os.path.join(logdir, 'pynhldb_error.log')
        file_error_handler = logging.handlers.TimedRotatingFileHandler(
            error_log, when='midnight', interval=1)
        file_error_handler.setFormatter(file_formatter)
        file_error_handler.setLevel(logging.ERROR)
        handlers.append(file_error_handler)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for handler in handlers:
        logger.addHandler(handler)
