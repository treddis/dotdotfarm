#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

""" Usefool tools for project """

from colorama import Fore, Style
from tqdm import tqdm
from dotdotfarm.engines.http_engine import HttpResponse

def print_http_result(future):
	result = future.result()
	if type(result) == HttpResponse:
		tqdm.write(' {:<100}{:>20}'.format(result.payload, # TODO: add more informative output
	                                                 f' [Status: {Fore.GREEN}{result.status}{Style.RESET_ALL}, Size: {len(result.data)}]'))

def get_add_file(files_dict):
	def add_file(future):
		result = future.result()
		if type(result) == HttpResponse:
			data = result.data.decode()
			if data not in files_dict.values():
				files_dict[result.url] = data
	return add_file