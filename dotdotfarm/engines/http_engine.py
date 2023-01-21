#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import asyncio
import aiohttp
import tqdm.auto
from collections import namedtuple

HttpResponse = namedtuple('HTTP_RESPONSE', 'url status headers text payload')


class HTTPEngine:

	def __init__(self, url, method, headers, data, payloads,
		limit=1000,
		requests_limit=0,
		status_manager=tqdm.asyncio.tqdm,
		allow_redirects=False,
		verify_ssl=True,
		print_callback=None,
		filters=None):
		self.url = url
		self.method = method
		self.headers = headers
		self.data = data
		self.payloads = payloads
		self.limit = limit
		self.status_manager = status_manager
		self.allow_redirects = allow_redirects
		self.verify_ssl = verify_ssl
		self.print_callback = print_callback

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
				connector=aiohttp.TCPConnector(limit=self.limit)) as session:	# accelerator
				for payload in self.payloads:
					if payload.type_ == 'url':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, self.method, payload.value, self.headers, self.data, payload.payload)))
					elif payload.type_ == 'header':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, self.method, self.url, payload.value, self.data, payload.payload)))
					elif payload.type_ == 'data':
						self.tasks.append(
							asyncio.create_task(
								self.request(
									session, self.method, self.url, self.headers, payload.value, payload.payload)))
					self.tasks[-1].add_done_callback(self.print_callback)

				# for task in self.status_wrapped(self.tasks, ascii=True, position=35):
				# 	await self.oqueue.put(await task) # !!!
				await asyncio.gather(*self.tasks)

		except asyncio.CancelledError:
			return
		except ConnectionResetError:
			return
		except BaseException:
			return
		finally:
			for task in self.tasks:
				task.cancel()
			# self.oqueue.task_done()

	async def request(self, session, method, url, headers, data, used_payload):
		try:
			async with session.request(method, url,
				headers=headers, data=data,
				verify_ssl=self.verify_ssl,
				allow_redirects=self.allow_redirects) as response:
				text = await response.read()
				resp = HttpResponse(url, response.status, response.headers, text, used_payload)
		except asyncio.CancelledError:
			return
		except asyncio.TimeoutError:
			return
		except aiohttp.client_exceptions.ClientConnectorError:
			return
		except BaseException:
			return

		return self.filtered(resp)

	def filtered(self, response):
		""" Filters response based on user rules """

		# while (response := await self.oqueue.get()) != None:
		# 	# text = await response.text.read()
		if response.status not in self.fc and len(response.text) not in self.fs:
			return response