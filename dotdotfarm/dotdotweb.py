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

argparse_list = partial(str.split, sep=',')


async def get_http(session, url, save, headers={}):
    try:
        async with session.get(url, verify_ssl=False, headers=headers) as response:
            text = await response.read()
            if response.status == 200:
                if len(text) not in opts.fs:
                    print('{:<100}{:>20}'.format(str(url), # TODO: add more informative output
                                                 f' [Status: {Fore.GREEN}200{Style.RESET_ALL}, Size: {len(text)}]'))
                if opts.output_data:
                    save[url.path] = f'{Back.WHITE}{Fore.BLACK}{text.decode()}{Style.RESET_ALL}'
            elif response.status in (301, 403, 404):
                if len(text) not in opts.fs and opts.verbose:
                    print('{:<100}{:>20}'.format(str(url),
                                                 f' [Status: {Fore.YELLOW}{response.status}{Style.RESET_ALL}, Size: {len(text)}]'))
            elif response.status in (500,):
                if len(text) not in opts.fs and opts.verbose:
                    print('{:<100}{:>20}'.format(str(url),
                                                 f' [Status: {Fore.RED}{response.status}{Style.RESET_ALL}, Size: {len(text)}]'))
            else:
                if len(text) not in opts.fs and opts.verbose:
                    print('{:<100}{:>20}'.format(str(url), f' [Status: {response.status}, Size: {len(text)}]'))

            return response
    except asyncio.CancelledError:
        raise
    except aiohttp.client_exceptions.ClientConnectorError:
        return
    except aiohttp.client_exceptions.ServerTimeoutError:
        return 
    except BaseException:
        raise


async def post_http(url, save):
    pass


async def run_http_engine(url, save, headers=None, data=None):
    # TODO: make fast & scalable HTTP/S engine in async manner
    # TODO: add Golang transport for speed up networking
    # session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
    results = []
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=1650)) as session:  # speed up requests with increasing simultaneous TCP connections
            # print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Generating requests')
            tasks = []
            if type(url) == list:
                for u in url:
                    u = yarl.URL(u, encoded=True)
                    tasks.append(asyncio.create_task(get_http(session, u, save)))
            else:
                url = yarl.URL(url, encoded=True)
                for header in headers:
                    header = dict([header.split(': ')])
                    tasks.append(asyncio.create_task(get_http(session, url, save, header)))
            # print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Starting event loop')
            for task in tqdm.asyncio.tqdm.as_completed(tasks):
                results.append(await task)
    except asyncio.exceptions.CancelledError:
        pass
    except aiohttp.client_exceptions.ClientConnectorError:
        print(f'[{Fore.RED}-{Style.RESET_ALL}] Host is not available: connection refused') # TODO: add graceful shutdown after many reset errors
    except aiohttp.client_exceptions.ServerTimeoutError:
        print(f'[{Fore.RED}-{Style.RESET_ALL}] Host is not available: connection timeout') # TODO: add graceful shutdown after many timeout errors
    finally:
        for task in tasks:
            task.cancel()
        return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path traversal identificator & exploit')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    # parser.add_argument('-M', '--module-detect', action='store_true', default=False, help='intelligent service detection')
    parser.add_argument('-o', '--os-type', required=True, choices=['windows', 'linux'])
    # parser.add_argument('-O', '--os-detect', action='store_true', default=False, help='intelligent OS detection') # TODO: add OS detection mechanisms
    parser.add_argument('-d', '--depth', type=int, default=4, help='depth of PT searching')
    parser.add_argument('-f', '--filename', help='specific filename for PT detection')
    parser.add_argument('--output-data', action='store_true', help='output contents of harvested files')
    parser.add_argument('-fs', type=argparse_list, default=[], help='filter output by size')
    parser.add_argument('-fc', type=argparse_list, default=[], help='filter output by response code')
    parser.add_argument('-H', '--header', nargs='+', help='fuzzing header')
    parser.add_argument('url', help='url for testing')

    opts = parser.parse_args() # TODO: fuzz input for robust CLI
    parsed_url = yarl.URL(opts.url)
    if opts.fs:
        opts.fs = list(map(int, opts.fs))
    if opts.header:
        if len(opts.header) > 1:
            parser.error('Not implemented')
        if opts.header[0].count('FUZZ') != 1:
            parser.error('You must specify FUZZ parameter in header by example Referer: https://google.com/path?param=FUZZ')
        input_str = opts.header[0]
    if opts.url.count('FUZZ') != 1 and not opts.header:
        parser.error('You must specify FUZZ parameter in url by example scheme://host:port/path?parameter=FUZZ')
    elif opts.url.count('FUZZ') == 1:
        input_str = opts.url

    # max_url_size = len(opts.url) + len(max(WINDOWS_FILES if opts.os_type == 'windows' else LINUX_FILES)) + len(
    #     max(DOTS)) * opts.depth + len(max(SLASHES)) * opts.depth

    generator = Generator(input_str, opts.depth, opts.os_type) # TODO: make fast & flexible payloads generator in async manner
    payloads = generator.get_words()

    saves = {} # TODO: make savings better
    loop = asyncio.new_event_loop()
    if yarl.URL(opts.url).scheme in ('http', 'https'):
        if opts.header:
            task = loop.create_task(run_http_engine(opts.url, saves, payloads))
        else:
            task = loop.create_task(run_http_engine(payloads, saves)) # TODO: use concurrent.futures.ProcessPoolExecutor for speed up
    else:
        parser.error('Not implemented')

    try:
        start = time.time()
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Started at {time.ctime(start)}')
        results = []
        results = loop.run_until_complete(task)
    except KeyboardInterrupt:
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Got keyboard interrupt')
        task.cancel()
        loop.run_until_complete(task)
    finally:
        amount = sum(map(lambda x: isinstance(x, aiohttp.ClientResponse) == True, results))
        if results:
            print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Amount of responsed queries: ' + \
                f'{amount} ({round(amount/len(results), 2) * 100})')
        loop.close()
        end = time.time()

        if opts.output_data:
            for k, v in saves.items():
                print(f'\t{k}\n{v}\n\n')
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Ended at {time.ctime(end)} ({int(end - start)} seconds)')
