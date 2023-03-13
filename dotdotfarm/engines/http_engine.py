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

HttpQuery = namedtuple('HTTP_QUERY', 'type_ value payload')
HttpResponse = namedtuple('HTTP_RESPONSE', 'url status headers data payload')


class HTTPEngine:

	def __init__(self, url, method, headers, data, payloads,
		limit=1000,
		status_manager=tqdm.asyncio.tqdm,
		allow_redirects=False,
		verify_ssl=False,
		timeout=60,
		callbacks=[],
		filters=None,
		delay=0):
		self.url = url
		self.method = method
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
				connector=aiohttp.TCPConnector(limit=self.limit)) as session:
				for payload in self.payloads:
					if payload.type_ == 'url':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, 'get', payload.value, self.headers, self.data, payload.payload)))
					elif payload.type_ == 'header':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, self.method, self.url, payload.value, self.data, payload.payload)))
					elif payload.type_ == 'data':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, 'post', self.url, self.headers, payload.value, payload.payload)))
					for callback in self.callbacks:
						self.tasks[-1].add_done_callback(callback)

				for task in self.status_wrapped(self.tasks):
					await task
					time.sleep(self.delay)

		except asyncio.CancelledError:
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

	async def request(self, session, method, url, headers, data, used_payload):
		url = yarl.URL(url, encoded=True)
		try:
			async with session.request(method, url,
									   headers=headers, data=data,
									   verify_ssl=self.verify_ssl,
									   allow_redirects=self.allow_redirects,
									   timeout=self.timeout) as response:
				text = await response.read()
				url = str(url)
				resp = HttpResponse(url, response.status, response.headers, text, used_payload)
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
		except BaseException:
			return


	def filtered(self, response):
		""" Filters response based on user rules """
		try:
			if response.status not in self.fc and len(response.data) not in self.fs:
				return dotdotfarm.callbacks.cobject.CallbackObject(response)  # return response from engine as callback-chain object
		except BaseException:
			return