#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
# import logging
import asyncio
import re

import yarl
import time
from functools import partial
from colorama import init, Fore, Style
init()

from dotdotfarm.generators.words_generator import Generator
from dotdotfarm.engines.http_engine import HTTPEngine
from dotdotfarm.callbacks.callbacks import print_http_result, add_file, validate_file

__version__ = '1.7.1'

argparse_list = partial(str.split, sep=',')

async def factory(engine):
    try:
        task = asyncio.get_running_loop().create_task(engine.run())
        await task
    except asyncio.CancelledError:
        task.cancel()
    except ConnectionResetError:
        pass
    except BaseException as e:
        print(e)

def main():
    print(f"""{Fore.CYAN}
    .___      __      .___      __    {Fore.RED}_____                      
  {Fore.CYAN}__| _/{Fore.YELLOW}____{Fore.CYAN}_/  |_  __| _/{Fore.YELLOW}____{Fore.CYAN}_/  |__{Fore.RED}/ ____\\____ _______  _____  
 {Fore.CYAN}/ __ |{Fore.YELLOW}/  _ \\{Fore.CYAN}   __\\/ __ |{Fore.YELLOW}/  _ \\{Fore.CYAN}   __{Fore.RED}\\   __\\\\__  \\\\_  __ \\/     \\ 
{Fore.CYAN}/ /_/ {Fore.YELLOW}(  <_> ){Fore.CYAN}  | / /_/ {Fore.YELLOW}(  <_> ){Fore.CYAN}  |  {Fore.RED}|  |   / __ \\|  | \\/  Y Y  \\
{Fore.CYAN}\\____ |{Fore.YELLOW}\\____/{Fore.CYAN}|__| \\____ |{Fore.YELLOW}\\____/{Fore.CYAN}|__|  {Fore.RED}|__|  (____  /__|  |__|_|  /
     {Fore.CYAN}\\/                \\/                       {Fore.RED}\\/            \\/ 
     {Style.RESET_ALL}""")

    parser = argparse.ArgumentParser(description='fast path traversal identificator & exploit')
    parser.add_argument('--version', action='version', version=f'dotdotweb {__version__}', help='print version of the tool')
    parser.add_argument('--proxy', default='', help='specify proxy to test selected url')

    # Callbacks
    callbacks = parser.add_argument_group('Callbacks')
    callbacks.add_argument('-V', '--validate', action='store_true', help='validate files\' content after successfull exploitation (default false)')
    # parser.add_argument('-v', '--verbose', action='store_true', help='verbose output of responses')
    # parser.add_argument('--debug', action='store_true', help='debug output')
    callbacks.add_argument('-A', '--all', action='store_true', help='try all files after successfull exploitation (default false)')
    callbacks.add_argument('-P', '--print-files', action='store_true', help='read traversed files (default false)')
    # parser.add_argument('-M', '--module-detect', action='store_true', default=False, help='intelligent service detection')

    # Parameters for payload generator
    generator = parser.add_argument_group('Payload generator parameters')
    generator.add_argument('-o', '--os-type', choices=['windows', 'linux'], default='', help='target OS type (default all)')
    generator.add_argument('-d', '--depth', type=int, default=5, help='depth of PT searching (default 5)')
    generator.add_argument('-f', '--file', help='specific file for PT detection')

    # Timings
    parser.add_argument('--rate', type=int, default=0, help='limit requests per second (default 0)')
    parser.add_argument('-t', '--timeout', type=int, default=60, help='timeout of connections (default 60)')

    # Filters
    filters = parser.add_argument_group('Filters')
    filters.add_argument('-fs', type=argparse_list, default=[], help='filter output by size (with quantifiers)')
    filters.add_argument('-fc', type=argparse_list, default=[], help='filter output by response code (with quantifiers)')

    # Payload specificators
    locations = parser.add_argument_group('Payload locations')
    locations.add_argument('--method', help='custom method for requests')
    locations.add_argument('--header', dest='headers', default=[], action='append', help='custom header for requests')
    locations.add_argument('--data', default='', help='specify POST data')
    locations.add_argument('url', help='target URL')

    opts = parser.parse_args()
    # if opts.debug:
    #     logging.getLogger("asyncio").setLevel(logging.WARNING)

    if opts.fs:
        if not all(map(lambda x: re.match(r'[0-9\*\?]+', x), opts.fs)):
            parser.error('Invalid -fs parameter')
        else:
            opts.fs = list(map(lambda x: x.replace("*", "\\d*").replace("?", "\\d?"), opts.fs))
    if opts.fc:
        if not all(map(lambda x: re.match(r'[0-9\*\?]+', x), opts.fc)):
            parser.error('Invalid -fc parameter')
        else:
            opts.fc = list(map(lambda x: x.replace("*", "\\d*").replace("?", "\\d?"), opts.fc))
    if opts.proxy:
        if not re.match(r'^(socks(5|4)|https?)://(\S+:\S+@)?(([0-9]\.){3}[0-9]{1,3}|[a-zA-Z0-9-.]{1,255})(:\d+)?\/?$', opts.proxy):
            parser.error('Invalid --proxy parameter')
        # opts.fc = list(map(int, opts.fc))

    if 'FUZZ' not in opts.url and 'FUZZ' not in opts.data and not any(map(lambda x: 'FUZZ' in x, opts.headers)):
        parser.error('You must specify FUZZ parameter in URL/Header/Data by example Referer: https://google.com/path?param=FUZZ')
    inputs = {}
    if 'FUZZ' in opts.url:
        inputs['url'] = [opts.url]
    if 'FUZZ' in opts.data:
        inputs['data'] = [opts.data]
    for header in opts.headers:
        if 'FUZZ' in header:
            if 'header' in inputs:
                inputs['header'].append(header)
            else:
                inputs['header'] = [header]

    generator = Generator('http', inputs, opts.depth, opts.os_type, custom_file=opts.file)
    payloads = generator.get_payloads()

    loop = asyncio.new_event_loop()
    if yarl.URL(opts.url).scheme in ('http', 'https'):
        headers = dict((header.split(': ') for header in opts.headers if header.count('FUZZ') == 0))

        callbacks = []
        if opts.validate:
            callbacks.append(validate_file(False if opts.all else True))
        callbacks.append(print_http_result)
        if opts.print_files:
            files = {}
            callbacks.append(add_file(files))
        engine = HTTPEngine(
            opts.url,
            opts.method, headers, opts.data,
            payloads,
            callbacks=callbacks,
            filters=(opts.fc, opts.fs),
            timeout=opts.timeout,
            rate=opts.rate,
            proxy=opts.proxy)

        task = loop.create_task(factory(engine))
    else:
        parser.error('This URL scheme is not implemented yet')

    try:
        start = time.time()
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Started at {time.ctime(start)}')
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print(f'\n[{Fore.CYAN}*{Style.RESET_ALL}] Got keyboard interrupt')
        task.cancel()
        loop.run_until_complete(task)
    finally:
        loop.close()
        end = time.time()

        if opts.print_files:
            for k, v in files.items():
                print('\n\n\t' + f'{Fore.YELLOW}-{Fore.RED}+' * 10 + f' {Style.RESET_ALL}{k} ' + f'{Fore.RED}+{Fore.YELLOW}-' * 10 + '\n' + f'{Style.RESET_ALL}\n{v}\n')
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Ended at {time.ctime(end)} ({int(end - start)} seconds)')

if __name__ == '__main__':
    main()
