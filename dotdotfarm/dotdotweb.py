#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
import asyncio
import aiohttp
import yarl
import time
import tqdm.asyncio
from functools import partial
from colorama import init, Fore, Back, Style
init()

from generator.words_generator import Generator
from engines.http_engine import HTTPEngine
from tools import print_http_result

argparse_list = partial(str.split, sep=',')


async def main(engine):
    # TODO: add Golang transport for speed up networking    
    try:
        task = asyncio.create_task(engine.run())
        await task
        # results = []
        # async for result in engine.filtered_results(fc, fs):
        #     # print('{:<100}{:>20}'.format(result.payload, # TODO: add more informative output
        #     #                                      f' [Status: {Fore.GREEN}{result.status}{Style.RESET_ALL}, Size: {len(result.text)}]'))
        #     results.append(result)
    except asyncio.CancelledError:
        task.cancel()
    except ConnectionResetError:
        pass
    # else:
    #     amount = sum(map(lambda x: x.status == 200, results))
    #     if results:
    #         print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Amount of responsed queries: ' + \
    #             f'{amount} ({round(amount/len(results), 2) * 100})')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path traversal identificator & exploit')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    # parser.add_argument('-M', '--module-detect', action='store_true', default=False, help='intelligent service detection')
    parser.add_argument('-o', '--os-type', required=True, choices=['windows', 'linux'])
    # parser.add_argument('-O', '--os-detect', action='store_true', default=False, help='intelligent OS detection') # TODO: add OS detection mechanisms
    parser.add_argument('-D', '--depth', type=int, default=4, help='depth of PT searching')
    parser.add_argument('-f', '--filename', help='specific filename for PT detection')
    parser.add_argument('--output-data', action='store_true', help='output contents of harvested files')
    parser.add_argument('-fs', type=argparse_list, default=[], help='filter output by size')
    parser.add_argument('-fc', type=argparse_list, default=[], help='filter output by response code')
    parser.add_argument('-H', '--header', dest='headers', default=[], action='append', help='specify header for requests')
    parser.add_argument('-d', '--data', default='', help='specify POST data')
    parser.add_argument('-m', '--method', choices=['get', 'post', 'put', 'trace', 'delete'], default='get',
        help='used HTTP method for requests')
    parser.add_argument('url', help='url for testing')

    opts = parser.parse_args() # TODO: fuzz input for robust CLI

    if opts.fs:
        opts.fs = list(map(int, opts.fs))
    if opts.fc:
        opts.fc = list(map(int, opts.fc))

    # match 'FUZZ':
    #     case opts.url:
    #         pass
    #     case opts.header:
    #         pass
    #     case opts.data:
    #         pass
    #     case _:
    #         parser.error('You must specify FUZZ parameter in URL/Header/Data by example Referer: https://google.com/path?param=FUZZ')

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

    # max_url_size = len(opts.url) + len(max(WINDOWS_FILES if opts.os_type == 'windows' else LINUX_FILES)) + len(
    #     max(DOTS)) * opts.depth + len(max(SLASHES)) * opts.depth

    generator = Generator('http', inputs, opts.depth, opts.os_type)
    payloads = generator.get_payloads()

    # saves = {} # TODO: make savings better
    loop = asyncio.new_event_loop()
    if yarl.URL(opts.url).scheme in ('http', 'https'):
        headers = dict((header.split(': ') for header in opts.headers if header.count('FUZZ') == 0))

        engine = HTTPEngine(
            opts.url, opts.method,
            headers, opts.data,
            payloads,
            print_callback=print_http_result,
            filters=(opts.fc, opts.fs))

        task = loop.create_task(main(engine)) # TODO: use concurrent.futures.ProcessPoolExecutor for speed up
    else:
        parser.error('Not implemented')

    try:
        start = time.time()
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Started at {time.ctime(start)}')
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Got keyboard interrupt')
        task.cancel()
        loop.run_until_complete(task)
    finally:
        loop.close()
        end = time.time()

        if opts.output_data:
            for k, v in saves.items():
                print(f'\t{k}\n{v}\n\n')
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Ended at {time.ctime(end)} ({int(end - start)} seconds)')
