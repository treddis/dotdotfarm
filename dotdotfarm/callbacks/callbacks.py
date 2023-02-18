#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

from colorama import Fore, Style
from tqdm import tqdm
from dotdotfarm.engines.http_engine import HttpResponse

def print_http_result(future):
	try:
		result = future.result()
		if type(result) == HttpResponse:
			tqdm.write(' {:<100}{:>20}'.format(result.payload,
														 f' [Status: {Fore.GREEN}{result.status}{Style.RESET_ALL}, Size: {len(result.data)}]'))
	except:
		tqdm.write(' {:<100}{:>20}'.format(f' [Status: {Fore.RED}ERROR{Style.RESET_ALL}, Size: {len(result.data)}]'))

def get_add_file(files_dict):
	def add_file(future):
		result = future.result()
		if type(result) == HttpResponse:
			data = result.data.decode()
			if data not in files_dict.values():
				files_dict[result.url] = data
	return add_file