#!/usr/bin/env python3
# ! -*- coding: utf-8 -*-

import re
from colorama import Fore, Style
from tqdm import tqdm

import dotdotfarm.engines.http_engine
import dotdotfarm.generators.words_generator
from dotdotfarm.callbacks.cobject import Failed


def print_http_result(future):
    """ Basic callback for printing result of request. """
    try:
        cobject = future.result()
        if cobject.state == Failed:
            return
        if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
            tqdm.write(' {:<100}{:>20}'.format(cobject.response.payload,
                                               f' [Status: {Fore.GREEN}{cobject.response.status}{Style.RESET_ALL}, Size: {len(cobject.response.data)}]'))
    except BaseException:
        # tqdm.write('{:<10}'.format(f'{Fore.RED}ERROR{Style.RESET_ALL}'))
        return


def validate_file(future):
    """ This callback is used for checking files' content. """
    try:
        cobject = future.result()
        if cobject.state == Failed:
            return
        if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
            data = cobject.response.data.decode()
        if not any(map(lambda x: re.match(x, data) != None,
                       dotdotfarm.generators.words_generator.LINUX_FILES_REGEXP + \
                       dotdotfarm.generators.words_generator.WINDOWS_FILES_REGEXP)):
            cobject.state = Failed
    except:
        # tqdm.write('{:<10}'.format(f'{Fore.RED}ERROR{Style.RESET_ALL}'))
        return

def add_file(files_dict):
    """ This callback is used for saving data from response. """
    def add(future):
        try:
            cobject = future.result()
            if cobject.state == Failed:
                return cobject
            if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
                data = cobject.response.data.decode()
            elif type(cobject.response) == WsResponse:
                data = cobject.response.data
            if data not in files_dict.values():
                files_dict[cobject.url] = data
        except:
            # tqdm.write('{:<10}'.format(f'{Fore.RED}ERROR{Style.RESET_ALL}'))
            return
    return add


def exec():
    pass
