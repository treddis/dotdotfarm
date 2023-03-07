#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
import logging
import asyncio
import yarl
import time
from functools import partial
from colorama import init, Fore, Style
init()

from dotdotfarm.generators.words_generator import Generator
from dotdotfarm.engines.http_engine import HTTPEngine
from dotdotfarm.callbacks.callbacks import print_http_result, add_file, validate_file

VERSION = "1.4.1"

argparse_list = partial(str.split, sep=',')

async def factory(engine):
    try:
        task = asyncio.create_task(engine.run())
        await task
    except asyncio.CancelledError:
        task.cancel()
    except ConnectionResetError:
        pass
    except BaseException:
        pass

def main():
    print(f"""{Fore.CYAN}
    .___      __      .___      __    {Fore.RED}_____                      
  {Fore.CYAN}__| _/{Fore.YELLOW}____{Fore.CYAN}_/  |_  __| _/{Fore.YELLOW}____{Fore.CYAN}_/  |__{Fore.RED}/ ____\\____ _______  _____  
 {Fore.CYAN}/ __ |{Fore.YELLOW}/  _ \\{Fore.CYAN}   __\\/ __ |{Fore.YELLOW}/  _ \\{Fore.CYAN}   __{Fore.RED}\\   __\\\\__  \\\\_  __ \\/     \\ 
{Fore.CYAN}/ /_/ {Fore.YELLOW}(  <_> ){Fore.CYAN}  | / /_/ {Fore.YELLOW}(  <_> ){Fore.CYAN}  |  {Fore.RED}|  |   / __ \\|  | \\/  Y Y  \\
{Fore.CYAN}\\____ |{Fore.YELLOW}\\____/{Fore.CYAN}|__| \\____ |{Fore.YELLOW}\\____/{Fore.CYAN}|__|  {Fore.RED}|__|  (____  /__|  |__|_|  /
     {Fore.CYAN}\\/                \\/                       {Fore.RED}\\/            \\/ 
     {Style.RESET_ALL}""")

    parser = argparse.ArgumentParser(description='path traversal identificator & exploit')
    parser.add_argument('-V', '--version', action='version', version=f'dotdotweb {VERSION}', help='print version of the tool')
    parser.add_argument('--debug', action='store_true', help='debug output')
    # parser.add_argument('-M', '--module-detect', action='store_true', default=False, help='intelligent service detection')
    parser.add_argument('-o', '--os-type', choices=['windows', 'linux'], default='')
    # parser.add_argument('-O', '--os-detect', action='store_true', default=False, help='intelligent OS detection') # TODO: add OS detection mechanisms
    parser.add_argument('-D', '--depth', type=int, default=5, help='depth of PT searching, default is 5')
    parser.add_argument('--timeout', type=int, default=60, help='timeout of connections')
    parser.add_argument('-f', '--file', help='specific file for PT detection')
    parser.add_argument('-R', '--print-files', action='store_true', help='read traversed files')
    parser.add_argument('-fs', type=argparse_list, default=[], help='filter output by size')
    parser.add_argument('-fc', type=argparse_list, default=[], help='filter output by response code')
    parser.add_argument('-H', '--header', dest='headers', default=[], action='append', help='specify header for requests')
    parser.add_argument('-d', '--data', default='', help='specify POST data')
    parser.add_argument('-m', '--method', choices=['get', 'post', 'put', 'trace', 'delete'], default='', help='used HTTP method for requests')
    parser.add_argument('url', help='url for testing')

    opts = parser.parse_args()
    if opts.debug:
        logging.getLogger("asyncio").setLevel(logging.WARNING)

    if opts.fs:
        opts.fs = list(map(int, opts.fs))
    if opts.fc:
        opts.fc = list(map(int, opts.fc))
    if opts.data and not opts.method:
        opts.method = 'post'
    elif not opts.method:
        opts.method = 'get'

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

        callbacks = [print_http_result, validate_file]
        if opts.print_files:
            files = {}
            callbacks.append(add_file(files))
        engine = HTTPEngine(
            opts.url, opts.method,
            headers, opts.data,
            payloads,
            callbacks=callbacks,
            filters=(opts.fc, opts.fs),
            timeout=opts.timeout)

        task = loop.create_task(factory(engine)) # TODO: use concurrent.futures.ProcessPoolExecutor for speed up
    else:
        parser.error('Not implemented')

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
                print('\n\n\t' + f'{Fore.YELLOW}-{Fore.RED}+' * 10 + f'{Style.RESET_ALL} ' + k + f' {Fore.RED}+{Fore.YELLOW}-' * 10 + '\n' + f'{Style.RESET_ALL}\n{v}\n\t' + f'{Fore.YELLOW}-{Fore.RED}+' * 70 + f'{Fore.YELLOW}-{Style.RESET_ALL}')
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Ended at {time.ctime(end)} ({int(end - start)} seconds)')

if __name__ == '__main__':
    main()
