#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

""" Usefool tools for project """

from colorama import Fore, Style
from dotdotfarm.engines.http_engine import HttpResponse

def print_http_result(future):
	result = future.result()
	if type(result) == HttpResponse:
		print(' {:<100}{:>20}'.format(result.payload, # TODO: add more informative output
	                                                 f' [Status: {Fore.GREEN}{result.status}{Style.RESET_ALL}, Size: {len(result.text)}]'))
