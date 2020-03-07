#!/usr/bin/env python3

from tabulate import tabulate

from app import logging

with open('access_log.txt', 'a') as logfile:
    data = list(logging.get_last_logs())
    logfile.write(tabulate(data))
    logfile.write('\n')
