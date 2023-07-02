#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import asyncio
import time
import aiohttp
import tqdm.auto
import yarl
from collections import namedtuple
from colorama import Fore, Style

import dotdotfarm.callbacks.cobject

HttpQuery = namedtuple('HTTP_QUERY', 'type_ fuzzed payload file')
HttpResponse = namedtuple('HTTP_RESPONSE', 'url status headers data payload file')


class HTTPEngine:

	def __init__(self, url, headers, data, payloads,
		limit=1000,
		status_manager=tqdm.asyncio.tqdm,
		allow_redirects=False,
		verify_ssl=False,
		timeout=60,
		callbacks=[],
		filters=None,
		delay=0):
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
		self.delay = delay

		self.fc = filters[0]
		self.fs = filters[1]

		# self.oqueue = asyncio.Queue()
		self.tasks = []

		if self.status_manager == tqdm.auto.asyncio_tqdm:
			self.status_wrapped = tqdm.auto.asyncio_tqdm.as_completed
		else:
			raise ValueError

	async def run(self):
		try:
			async with aiohttp.ClientSession(
					connector=aiohttp.TCPConnector(limit=self.limit),
					timeout=aiohttp.ClientTimeout(sock_connect=self.timeout)) as session:

				# Check if server is available
				try:
					async with session.get(self.url) as response:
						pass
				except aiohttp.client_exceptions.ClientConnectorError as e:
					print(f'[{Fore.RED}-{Style.RESET_ALL}] Connection error: {e.strerror}')
					await aiohttp.TCPConnector().close()
					return

				for payload in self.payloads:
					if payload.type_ == 'url':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, 'GET', payload.fuzzed,
									headers=self.headers,
									data=self.data,
									payload=payload.payload,
									file=payload.file)))
					elif payload.type_ == 'header':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session,
									'POST' if self.data else 'GET',
									self.url,
									headers=payload.fuzzed,
									data=self.data,
									payload=payload.payload,
									file=payload.file)))
					elif payload.type_ == 'data':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, 'POST', self.url,
									headers=self.headers,
									data=payload.fuzzed,
									payload=payload.payload,
									file=payload.file)))
					for callback in self.callbacks:
						self.tasks[-1].add_done_callback(callback)

				for task in self.status_wrapped(self.tasks):
					await task
					time.sleep(self.delay)

		except (asyncio.CancelledError, KeyboardInterrupt):
			pass
		except asyncio.TimeoutError:
			print(f'[{Fore.RED}-{Style.RESET_ALL}] Timeout occurred')
			await aiohttp.TCPConnector().close()
		except ConnectionResetError:
			return
		except BaseException:
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
			async with session.request(method, url,
									   headers=headers, data=data,
									   verify_ssl=self.verify_ssl,
									   allow_redirects=self.allow_redirects) as response:
				text = await response.read()
				url = str(url)
				resp = HttpResponse(url, response.status, response.headers, text, payload, file)
				return self.filtered(resp)
		except asyncio.TimeoutError:
			raise
		except (
				asyncio.CancelledError,
				aiohttp.client_exceptions.ClientConnectorError,
				aiohttp.ClientOSError,
				aiohttp.ServerDisconnectedError,
				):
			return
			# return HttpResponse(url, None, None, None, None)
		except ConnectionResetError:
			return
		except KeyboardInterrupt:
			raise
		except BaseException:
			return


	def filtered(self, response):
		""" Filters response based on user rules """
		try:
			if response.status not in self.fc and len(response.data) not in self.fs:
				return dotdotfarm.callbacks.cobject.CallbackObject(response)  # return response from engine as callback-chain object
		except BaseException:
			return