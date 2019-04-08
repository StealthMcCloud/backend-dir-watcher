#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dirwatcher- Create a long running program
that searches a directories files for text files
containing an input string,
if found, log the txt file and line found.
use python dirwatcher.py {extension} {polling interval} {directory to search} {magic text}
"""

'''When I do a refactor try to elimate all the global variables except for the exit_flag'''

import os
import argparse
import time
import datetime
import logging
import signal

__author__ = "Clinton Johnson"


"""Boiler plate for logger on global/module level """
logger = logging.getLogger(__name__)

"""Exit flag part of sys.signal """
exit_flag = False
files_logged = []
found_text = {}

# def scan_file(file_name, starting_line, magic_text):
    '''open file to read
    enumerate through the lines in a file using a for loop
    When line number reaches starting line that is when you start searching for the magic_text
    Every time it finds the magic text in lines and subsequent lines it will log that it found the text.
    Return last line that was ended on.
    '''


def find_files(directory, extension, magictext):
    """Find all files in given directory, if dir exists"""
    global files_logged
    global found_text
    dir_path = os.path.abspath(directory)
    dir_files = os.listdir(dir_path)
    for file in dir_files:
        if file.endswith(extension) and file not in files_logged:
            logger.info('New file found: {}'.format(file))
            files_logged.append(file)
        if file.endswith(extension):
            file_path = os.path.join(dir_path, file)
            if find_string_in_files(file_path, magictext):
                break
    for file in files_logged:
        if file not in dir_files:
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


def logger_initiate():
    """Adjusts how info is displayed in log and sets default log"""
    logger.setLevel(logging.DEBUG)
    return logging.basicConfig(
        format=(
            '%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S')


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


def signal_handler(sig_num, frame):
    """Smooth exit from system"""
    global exit_flag
    logger.warn('Signal Recieved: {}'.format(str(sig_num)))
    if sig_num:
        exit_flag = True


def create_parser():
    """Create Parser that accepts {optional extension} {optional polling interval} {directory to search} {magic text}"""
    parser = argparse.ArgumentParser(description='Watching for files containing magictext')
    parser.add_argument('--ext', help='File extensions to filter on, default=.txt', default='.txt')
    parser.add_argument('--poll', help="Polling interval in seconds, default=1.0", type=float, default=1.0)
    parser.add_argument('directory', help='Directory to watch.')
    parser.add_argument('magictext', help='Text to search for within matching files.')
    return parser


def main():
    """Currently only prints the files in a directory with extention"""
    parser = create_parser()
    input_args = parser.parse_args()
    if not input_args:
        parser.print_usage()
        sys.exit(1)
    logger_initiate()
    start_time = datetime.datetime.now()
    logger_banner('Started', start_time)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info('Searching directory="{0}" ext="{1}" interval="{2}" text="{3}" '.format(input_args.directory, input_args.ext, input_args.poll, input_args.magictext))
    while not exit_flag:
        try:
            find_files(input_args.directory,
                       input_args.ext, input_args.magictext)
        except OSError as e:
            logger.error('Directory does not exist: {}'.format(e))
        except Exception as e:
            logger.error('Unknown/unhandled error: {}'.format(e))
        time.sleep(input_args.poll)

    total_time = datetime.datetime.now() - start_time
    logger_banner('Ended', total_time, start=False)


if __name__ == "__main__":
    """Accepts parser, initiates logger, runs banners"""
    main()