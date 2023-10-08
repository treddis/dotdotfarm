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
from dotdotfarm.callbacks.cobject import FailedCallback

HttpQuery = namedtuple('HTTP_QUERY', 'type_ fuzzed payload file')
HttpResponse = namedtuple('HTTP_RESPONSE', 'url status headers data payload file')


class HTTPEngine:

	def __init__(self, url, method, headers, data, payloads,
		limit=1000,
		status_manager=tqdm.asyncio.tqdm,
		allow_redirects=False,
		verify_ssl=False,
		timeout=60,
		callbacks=[],
		filters=None,
		rate=0):
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

		self.fc = filters[0]
		self.fs = filters[1]

		# self.oqueue = asyncio.Queue()
		self.tasks = []

		if self.status_manager == tqdm.auto.asyncio_tqdm:
			self.status_wrapped = tqdm.auto.asyncio_tqdm.as_completed
		else:
			raise ValueError

		if self.rate:
			self.semaphore = asyncio.Semaphore(self.rate)

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
					# await asyncio.sleep(self.delay)

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
		if self.rate:
			await self.semaphore.acquire()
		try:
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
		except asyncio.TimeoutError:
			raise
		except (
				asyncio.CancelledError,
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
		except RuntimeError:
			return
		except BaseException as e:
			return


	def filtered(self, response):
		""" Filters response based on user rules """
		try:
			if response.status not in self.fc and len(response.data) not in self.fs:
				return dotdotfarm.callbacks.cobject.CallbackObject(response)  # return response from engine as callback-chain object
		except BaseException:
			return