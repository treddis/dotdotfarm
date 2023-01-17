#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
import asyncio
import aiohttp
import yarl
import time
from functools import partial
from colorama import init, Fore, Back, Style
init()

from .word_generator import Generator

argparse_list = partial(str.split, sep=',')


async def get_http(session, url, save):
    try:
        async with session.get(url, verify_ssl=False) as response:
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
    except asyncio.CancelledError:
        return
    except aiohttp.ClientConnectorError:
        raise
    except BaseException:
        return


async def post_http(url, save):
    pass


async def run_http(urls, save):
    # TODO: make fast & scalable HTTP/S engine in async manner
    # TODO: add Golang transport for speed up networking
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                limit=1000)) as session:  # speed up requests with increasing simultaneous TCP connections
            tasks = []
            for url in urls:
                url = yarl.URL(url, encoded=True)
                tasks.append(asyncio.create_task(get_http(session, url, save)))
            await asyncio.gather(*tasks) # TODO: fetch all results for future handling
    except aiohttp.ClientConnectorError:
        print(f'[{Fore.RED}-{Style.RESET_ALL}] Specified host is not available') # TODO: disable program shutdown after receiving connection error
    except asyncio.CancelledError:
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Closing event loop')
    finally:
        for task in tasks:
            task.cancel()

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
    parser.add_argument('url', help='url for testing')

    opts = parser.parse_args() # TODO: fuzz input for robust CLI
    parsed_url = yarl.URL(opts.url)
    if opts.filename:
        WINDOWS_FILES = [opts.filename]
        LINUX_FILES = [opts.filename]
    if opts.fs:
        opts.fs = list(map(int, opts.fs))
    if opts.url.count('FUZZ') != 1:
        parser.error('You must specify FUZZ parameter in url by example scheme://host:port/path?parameter=FUZZ')

    # max_url_size = len(opts.url) + len(max(WINDOWS_FILES if opts.os_type == 'windows' else LINUX_FILES)) + len(
    #     max(DOTS)) * opts.depth + len(max(SLASHES)) * opts.depth
    
    generator = Generator(opts.url, opts.os_type) # TODO: make fast & flexible payloads generator in async manner
    payloads = generator.get_words()

    saves = {} # TODO: make savings better
    loop = asyncio.new_event_loop()
    if yarl.URL(opts.url).scheme in ('http', 'https'):
        task = loop.create_task(run_http(payloads, saves)) # TODO: use concurrent.futures.ProcessPoolExecutor for speed up
    else:
        parser.error('Not implemented')

    try:
        start = time.time()
        print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Started at {time.ctime(start)}')
        loop.run_until_complete(task) # TODO: add async tqdm
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
