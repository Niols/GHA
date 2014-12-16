#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#                                    GHA.py                                    #
#                                   by Niols                                   #
#                                                                              #
#  BEERWARE License:                                                           #
#  <niols@niols.net> wrote this file. As long as you retain this notice you    #
#  can do whatever you want with this stuff. If we meet some day, and you      #
#  think this stuff is worth it, you can buy me a beer in return.              #
#  –– Poul-Henning Kamp                                                        #
#                                                                              #
################################################################################

import argparse
from sys import argv
from json import loads, dumps

from FrontBot import *
from HooksHandler import *
import URLShortener

from GithubHooks import *


DESCRIPTION = '''GitHub Announcer


'''

parser = argparse.ArgumentParser(description=DESCRIPTION, prog=argv[0])

parser.add_argument('-lh', '--listen-host',
                    type = str,
                    help = 'the address where GHA will be listening')

parser.add_argument('-lp', '--listen-port',
                    type = int,
                    help = 'the port where GHA will be listening')

parser.add_argument('-ih', '--irc-host',
                    type = str,
                    help = 'the irc server\'s address')

parser.add_argument('-ip', '--irc-port',
                    type = int,
                    help = 'the irc server\'s port')

parser.add_argument('-ic', '--irc-chans',
                    nargs = '*',
                    help = 'the irc channels')

parser.add_argument('-in', '--irc-name',
                    type = str,
                    help = 'the bot\'s name')

parser.add_argument('-ea', '--export-arguments',
                    metavar='FILE',
                    type = str,
                    help = 'export arguments in the given file')

parser.add_argument('-ia', '--import-arguments',
                    metavar = 'FILE',
                    type = str, # à rendre plus précis
                    help = 'import arguments from the given file')

ARGS = parser.parse_args()

if ARGS.import_arguments:
    try:
        args = loads(open(ARGS.import_arguments).read())
        for arg in [ s for s in dir(ARGS) if s[0] != '_' ]:
            if arg in args and not getattr(ARGS, arg):
                setattr(ARGS, arg, args[arg])
    except IOError:
#        V.prnt('The file %s were not found' % (ARGS.import_arguments),
         exit(1)
    except:
#        V.prnt ('Error while importing arguments from file.', V.ERROR)
#        for line in format_exc().split('\n'):
#            if line:
#                V.prnt (line, V.ERROR)
        exit(1)

if not ARGS.listen_host:
#    V.prnt('No listen host given. Using 0.0.0.0.', V.WARNING)
    ARGS.listen_host = '0.0.0.0'

if not ARGS.listen_port:
#    V.prnt('No listen port given. Using 80.', V.WARNING)
    ARGS.listen_port = 80

if not ARGS.irc_host:
#    V.prnt('No IRC host given. Using localhost.', V.WARNING)
    ARGS.irc_host = 'localhost'

if not ARGS.irc_port:
#    V.prnt('No IRC Port given. Using 6667.', V.WARNING)
    ARGS.irc_port = 6667

if not ARGS.irc_chans:
#    V.prnt('No IRC Chans given.', V.WARNING)
    ARGS.irc_chans = []

if not ARGS.irc_name:
#    V.prnt('No IRC Name given. Using GHA.', V.WARNING)
    ARGS.irc_name = 'GHA'

if ARGS.export_arguments:
    args = {}
    for arg in [ s for s in dir(ARGS) if s[0] != '_' and s not in ['import_arguments', 'export_arguments'] ]:
        args[arg] = getattr(ARGS, arg)
    open(ARGS.export_arguments, 'w+').write(dumps(args, indent=4))
    exit(0)



hooks_queue = Queue ()
text_queue = Queue ()

HooksHandlerThread(ARGS.listen_host, ARGS.listen_port, [hooks_queue]).start()

F = FrontBot(ARGS.irc_host, ARGS.irc_port, ARGS.irc_chans, ARGS.irc_name, [text_queue])
FrontBotThread(F).start()

def irc_prnt (message):
    text_queue.put(('prnt', (message, None)))


while True:
    (headers, body) = hooks_queue.get()

    if 'X-Github-Event' in headers.keys():
        try:
            text_queue.put(('prnt', (GithubHooks.handle(headers, body),)))
        except:
            for line in format_exc().split('\n'):
                if line:
                    text_queue.put(('prnt', (line, ['niols'])))

    else:
        pass
#        V.prnt('Received invalid request.', V.WARNING)
