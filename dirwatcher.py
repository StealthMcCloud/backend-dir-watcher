#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dirwatcher- Create a long running program
that searches a directories files for text files
containing an input string,
if found, log the txt file and line found.
use python dirwatcher.py {search string} {file type} {directory to search}
"""

__author__ = "Clinton Johnson"

import os
import argparse
import time
import datetime
import logging
import signal

"""Boiler plate for logger on global/module level """
logger = logging.getLogger(__file__)
"""Exit flag part of sys.signal """
exit_flag = False
files_logged = []
found_text = {}


def find_files(directory, extension, magictext):
    """Find all files in given directory, if dir exists """
    global files_logged
    global found_text
    directory_abspath = os.path.abspath(directory)
    all_files_in_directory = os.listdir(directory_abspath)
    for file in all_files_in_directory:
        if file.endswith(extension) and file not in files_logged:
            logger.info('New file found: {}'.format(file))
            files_logged.append(file)
        if file.endswith(extension):
            file_path = os.path.join(directory_abspath, file)
            if find_string_in_files(file_path, magictext):
                break
    for file in files_logged:
        if file not in all_files_in_directory:
            logger.info('File deleted: {}'.format(file))
            files_logged.remove(file)
            found_text[file] = 0


def find_string_in_files(file, magictext):
    """Given single file, looks for text, stores in global dict for record"""
    global found_text
    file_base = os.path.basename(file)
    with open(file) as f:
        all_lines = f.readlines()
        for line_number, line in enumerate(all_lines):
            if magictext in line:
                if file_base not in found_text.keys():
                    found_text[file_base] = line_number
                if (line_number >= found_text[file_base]
                        and file_base in found_text.keys()):
                    logger.info('Text="{0}" file="{1}" '
                                'line: {2}'.format(magictext,
                                                   file_base,
                                                   line_number + 1))
                    found_text[file_base] += 1
                    return True


def log_config():
    """Adjusts how info is displayed in log"""
    return logging.basicConfig(
        format=(
            '%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S')


def log_set_level():
    """Sets defaulf log level"""
    logger.setLevel(logging.DEBUG)


def logger_banner(startorend, time, start=True):
    """Log banner start/end"""
    time_message = 'Time Started'
    if not start:
        time_message = 'Up time'
    return logger.info(
        '\n\n' +
        '-*'*30 +
        '-\n\n'
        ' {2} running file name: {0}\n'
        ' {3}: {1}\n\n'.format(__file__,
                               time, startorend, time_message)
        + '-*'*30 + '-\n'
    )


def logger_initiate():
    """Iniates the logger boiler plate"""
    log_config()
    log_set_level()


def signal_handler(sig_num, frame):
    """Smooth exit from system"""
    global exit_flag
    logger.warn('Signal Recieved: {}'.format(str(sig_num)))
    if sig_num:
        exit_flag = True


def create_parser():
    """Create Parser that accepts"""
    parser = argparse.ArgumentParser(description='Taking names')
    parser.add_argument('magictext', help='Text to search for')
    parser.add_argument(
        'extension', help='Type of tile extension to search')
    parser.add_argument('directory', help='Directory to watch')
    parser.add_argument(
        'poll', help="polling interval required: number of seconds",
        nargs='?', default=1)
    return parser


def main(input_args):
    """Currently only prints the files in a directory with extention"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    count = 0
    while not exit_flag:
        logger.debug('Searching file="{0}" ext="{1}" text="{2}" seconds={3}'
                     .format(input_args.directory, input_args.extension,
                             input_args.magictext, input_args.poll))
        try:
            # if os.path.isdir(input_args.directory):
            find_files(input_args.directory,
                       input_args.extension, input_args.magictext)
            count = 0
        except OSError as e:
            if not count:
                logger.error('Directory does not exist: {}'.format(e))
                count += 1
        except Exception as e:
            if not count:
                logger.error('Unknown/unhandled error: {}'.format(e))
        time.sleep(int(input_args.poll))


if __name__ == "__main__":
    """Accepts parser, initiates logger, runs banners"""
    # python dirwatcher.py 3 string '.txt' searchhere
    parser = create_parser()
    input_args = parser.parse_args()
    logger_initiate()
    start_time = datetime.datetime.now()
    logger_banner('Started', start_time)
    main(input_args)
    total_time = datetime.datetime.now() - start_time
    logger_banner('Ended', total_time, start=False)