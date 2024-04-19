#!/usr/bin/env python3
# ! -*- coding: utf-8 -*-

import asyncio
import re
import aiohttp
import tqdm.auto
import yarl
from collections import namedtuple
from colorama import Fore, Style
from aiohttp_socks import ProxyConnector, ProxyType

import dotdotfarm.callbacks.cobject
# from dotdotfarm.callbacks.cobject import FailedCallback

def parse_proxy(url):
    proxy_type = proxy[url.split('://')[0]]  # TODO: try make it via regex
    host = url.split('://')[1].split('@')[-1].split(':')[0]
    port = url.split('://')[1].split('@')[-1].split(':')[1].split('/')[0]
    username = re.match(r'.+://([^:]\S)+:', url)
    if username is not None:
        username = username.group().split('://')[1].replace(':', '')
    password = re.search(r'(?!://):\S+@', url)
    if password is not None:
        password = password.group()[1:-1]
    proxy_dict = {
        'scheme': proxy_type,
        'host': host,
        'port': port,
        'username': username,
        'password': password
    }

    return proxy_dict


HttpQuery = namedtuple('HTTP_QUERY', 'type_ fuzzed payload file')
HttpResponse = namedtuple('HTTP_RESPONSE', 'url status headers data payload file')
proxy = {
    'socks5': ProxyType.SOCKS5,
    'socks4': ProxyType.SOCKS4,
    'http': ProxyType.HTTP
}


class HTTPEngine:

    def __init__(self, url, method, headers, data, payloads,
                 limit: int = 1000,
                 status_manager=tqdm.asyncio.tqdm,
                 allow_redirects: bool = False,
                 verify_ssl: bool = False,
                 timeout: int = 60,
                 callbacks=[],
                 filters=None,
                 rate: int = 0,
                 proxy: str = ''):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.payloads = payloads
        self.limit = limit
        self.status_manager = status_manager
        self.allow_redirects = allow_redirects
        self.verify_ssl = verify_ssl
        self.callbacks = callbacks
        self.timeout = timeout
        self.rate = rate
        self.proxy = '' if not proxy else parse_proxy(proxy)

        self.fc = filters[0]
        self.fs = filters[1]

        self.tasks = []

        if self.status_manager == tqdm.auto.asyncio_tqdm:
            self.status_wrapped = tqdm.auto.asyncio_tqdm.as_completed
        else:
            raise ValueError

        if self.rate:
            self.semaphore = asyncio.Semaphore(self.rate)

    async def run(self):
        # if self.proxy.split('://')[0] not in ('socks5', 'socks4'):  # This fixes bug to create async object inside async functions
        #     self.connector = aiohttp.TCPConnector(limit=self.limit)
        # else:
        # urlparse() can't parse some urls containing login:password pairs, so make custom parsing of URL
        if self.proxy:
            self.connector = ProxyConnector(
                proxy_type=self.proxy['scheme'],
                host=self.proxy['host'],
                port=self.proxy['port'],
                username=self.proxy['username'],
                password=self.proxy['password'],
                rdns=True)  # aka 'socks5://user:password@127.0.0.1:1080'
        else:
            self.connector = aiohttp.TCPConnector(limit=self.limit)

        try:
            async with aiohttp.ClientSession(
                    connector=self.connector,
                    timeout=aiohttp.ClientTimeout(sock_connect=self.timeout)) as session:
                # Check if server is available
                try:
                    async with session.get(
                            yarl.URL(self.url).origin(),
                            verify_ssl=self.verify_ssl,
                            allow_redirects=False) as response:
                        # async with session.get(self.url) as response:
                        await response.read()
                except aiohttp.client_exceptions.ClientConnectorError as e:
                    print(
                        f'[{Fore.RED}-{Style.RESET_ALL}] Connection error while connecting to target: {e.args[-1].reason}')
                    await aiohttp.TCPConnector().close()
                    return
                except BaseException as e:
                    print(e)
                # Check proxy
                try:
                    response = await session.get(
                                                 yarl.URL(self.url).origin(),
                                                 verify_ssl=self.verify_ssl,
                                                 allow_redirects=False)
                    # async with session.get(self.url, proxy=self.proxy) as response:
                    await response.read()
                except aiohttp.client_exceptions.ClientConnectorError as e:
                    print(f'[{Fore.RED}-{Style.RESET_ALL}] Connection error while checking proxy: {e.args[-1].reason}')
                    await aiohttp.TCPConnector().close()
                    return
                except BaseException as e:
                    print(e)

                for payload in self.payloads:
                    if payload.type_ == 'url':
                        self.tasks.append(
                            asyncio.create_task(
                                self.request(
                                    session, self.method or 'GET', payload.fuzzed,
                                    headers=self.headers,
                                    data=self.data,
                                    payload=payload.payload,
                                    file=payload.file)))
                    elif payload.type_ == 'header':
                        self.tasks.append(
                            asyncio.create_task(
                                self.request(
                                    session,
                                    self.method or ('POST' if self.data else 'GET'),
                                    self.url,
                                    headers=payload.fuzzed,
                                    data=self.data,
                                    payload=payload.payload,
                                    file=payload.file)))
                    elif payload.type_ == 'data':
                        self.tasks.append(
                            asyncio.create_task(
                                self.request(
                                    session, self.method or 'POST', self.url,
                                    headers=self.headers,
                                    data=payload.fuzzed,
                                    payload=payload.payload,
                                    file=payload.file)))
                    for callback in self.callbacks:
                        self.tasks[-1].add_done_callback(callback)

                async for task in self.status_manager(self.tasks, unit=' req'):
                    await task

        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        except asyncio.TimeoutError:
            print(f'[{Fore.RED}-{Style.RESET_ALL}] Timeout occurred')
            await aiohttp.TCPConnector().close()
        except ConnectionResetError:
            return
        except AttributeError as e:
            return
        except BaseException as e:
            print(e)
            return
        finally:
            # print(f'[{Fore.CYAN}*{Style.RESET_ALL}] Cancelling tasks')
            for task in self.tasks:
                task.cancel()

    async def request(self, session, method, url, *,
                      headers, data, payload,
                      file):
        url = yarl.URL(url, encoded=True)
        try:
            if self.rate:
                await self.semaphore.acquire()
            async with session.request(method, url,
                                       headers=headers, data=data,
                                       verify_ssl=self.verify_ssl,
                                       allow_redirects=self.allow_redirects) as response:
                text = await response.read()
                if self.rate:
                    await asyncio.sleep(1)
                    self.semaphore.release()
                url = str(url)
                resp = HttpResponse(url, response.status, response.headers, text, payload, file)
                return self.filtered(resp)
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError:
            raise
        except (
                aiohttp.client_exceptions.ClientConnectorError,
                aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError,
                aiohttp.ClientPayloadError):
            pass
            # return HttpResponse(url, None, None, None, None)
        except ConnectionResetError:
            return
        except KeyboardInterrupt:
            raise
        except RuntimeError as e:
            print(e)
            return
        except BaseException as e:
            print(e)
            return

    def filtered(self, response):
        """ Filters response based on user rules """
        try:
            if not any(map(lambda x: re.match(x, str(response.status)), self.fc)) and \
                    not any(map(lambda x: re.match(x, str(len(response.data))), self.fs)):
                # if response.status not in self.fc and len(response.data) not in self.fs:
                return dotdotfarm.callbacks.cobject.CallbackObject(
                    response)  # return response from engine as callback-chain object
        except BaseException:
            return
