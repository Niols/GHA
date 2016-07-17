#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
#                                    GHA.py                                   #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################

import argparse
import logging
from sys import argv
from json import loads, dumps
from os import getpid

from FrontBot import *
from HooksHandler import *

from GitHubHooks import *
import GitLabHooks

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(filename)s '
                           'line %(lineno)s | %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

logging.info('Starting')

DESCRIPTION = '''Github Announcer


'''

parser = argparse.ArgumentParser(description=DESCRIPTION, prog=argv[0])

parser.add_argument('-lh', '--listen-host',
                    type=str,
                    help='the address where GHA will be listening')

parser.add_argument('-lp', '--listen-port',
                    type=int,
                    help='the port where GHA will be listening')

parser.add_argument('-ih', '--irc-host',
                    type=str,
                    help='the irc server\'s address')

parser.add_argument('-ip', '--irc-port',
                    type=int,
                    help='the irc server\'s port')

parser.add_argument('-ic', '--irc-chans',
                    nargs='*',
                    help='the irc channels')

parser.add_argument('-in', '--irc-name',
                    type=str,
                    help='the bot\'s name')

parser.add_argument('-ea', '--export-arguments',
                    metavar='FILE',
                    type=str,
                    help='export arguments in the given file')

parser.add_argument('-ia', '--import-arguments',
                    metavar='FILE',
                    type=str,  # à rendre plus précis
                    help='import arguments from the given file')

parser.add_argument('--write-pid',
                    metavar='FILE',
                    type=str,
                    help='write all threads pids in given file')

parser.add_argument('-re', '--report-errors',
                    metavar='NICK',
                    type=str,
                    help='Report errors to the given person')

ARGS = parser.parse_args()

if ARGS.import_arguments:
    try:
        args = loads(open(ARGS.import_arguments).read())
        for arg in [s for s in dir(ARGS) if s[0] != '_']:
            if arg in args and not getattr(ARGS, arg):
                setattr(ARGS, arg, args[arg])
    except IOError:
        logging.error('The file %s were not found', ARGS.import_arguments)
        exit(1)
    except:
        logging.error('Error while importing arguments from file.')
        for line in format_exc().split('\n'):
            if line:
                logging.error(line)
        exit(1)

if not ARGS.listen_host:
    logging.info('No listen host given. Using 0.0.0.0.')
    ARGS.listen_host = '0.0.0.0'

if not ARGS.listen_port:
    logging.info('No listen port given. Using 80.')
    ARGS.listen_port = 80

if not ARGS.irc_host:
    logging.info('No IRC host given. Using localhost.')
    ARGS.irc_host = 'localhost'

if not ARGS.irc_port:
    logging.info('No IRC port given. Using 6667.')
    ARGS.irc_port = 6667

if not ARGS.irc_chans:
    logging.info('No IRC chans given.')
    ARGS.irc_chans = []

if not ARGS.irc_name:
    logging.info('No IRC name given. Using GHA.')
    ARGS.irc_name = 'GHA'

logging.info('Main thread\'s pid: %d' % (getpid(),))
if ARGS.write_pid:
    open(ARGS.write_pid, 'w').close()  # Shrink size to 0
    logging.debug('Writing main thread\'s pid in `%s`.' % ARGS.write_pid)
    open(ARGS.write_pid, 'a').write(str(getpid()) + '\n')


if ARGS.export_arguments:
    args = {}
    for arg in [
            s for s in dir(ARGS) if s[0] != '_'
            and s not in ['import_arguments', 'export_arguments']
            ]:
        args[arg] = getattr(ARGS, arg)
    open(ARGS.export_arguments, 'w+').write(dumps(args, indent=4))
    exit(0)


hooks_queue = Queue()
text_queue = Queue()

HHT = HooksHandlerThread(ARGS.listen_host, ARGS.listen_port, [hooks_queue])
HHT.start()

logging.info('HooksHandlerThread\'s pid: %d' % HHT.pid)
if ARGS.write_pid:
    logging.debug('Writing HooksHandlerThread\'s pid in `%s`.'
                  % ARGS.write_pid)
    open(ARGS.write_pid, 'a').write("%d\n" % HHT.pid)

FB = FrontBot(ARGS.irc_host, ARGS.irc_port, ARGS.irc_chans, ARGS.irc_name,
              [text_queue])
FBT = FrontBotThread(FB)
FBT.start()

logging.info('FrontBotThread\'s pid: %d' % FBT.pid)
if ARGS.write_pid:
    logging.debug('Writing FrontBotThread\'s pid in `%s`.' % ARGS.write_pid)
    open(ARGS.write_pid, 'a').write(str(FBT.pid) + '\n')


def irc_prnt(message):
    text_queue.put(('prnt', (message, None)))


while True:
    (headers, body) = hooks_queue.get()

    try:
        if 'X-Github-Event' in headers.keys():
            text_queue.put(('prnt', (GitHubHooks.handle(headers, body),)))

        else:
            text_queue.put(('prnt', (GitLabHooks.handle(headers, body),)))

    except:
        if ARGS.report_errors:
            for line in format_exc().split('\n'):
                if line:
                    text_queue.put(('prnt', (line, [ARGS.report_errors])))
