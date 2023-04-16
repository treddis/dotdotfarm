#!/usr/bin/env python3
# ! -*- coding: utf-8 -*-

import re
import asyncio
from colorama import Fore, Style
from tqdm import tqdm

import dotdotfarm.engines.http_engine
import dotdotfarm.generators.words_generator
from dotdotfarm.callbacks.cobject import Failed


def container(data):
    def decorator(fn):
        def wrapper(*args):
            fn()

        wrapper.attrib = data
        return wrapper

    return decorator


def print_http_result(future):
    """ Basic callback for printing result of request. """
    try:
        cobject = future.result()
        if cobject.state == Failed:
            return
        if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
            if cobject.response.status // 100 == 2:
                tqdm.write(' {:<100}{:>20}'.format(cobject.response.payload,
                                                   f' [Status: {Fore.GREEN}{cobject.response.status}{Style.RESET_ALL}, Size: {len(cobject.response.data)}]'))
            elif cobject.response.status // 100 == 5:
                tqdm.write(' {:<100}{:>20}'.format(cobject.response.payload,
                                                   f' [Status: {Fore.RED}{cobject.response.status}{Style.RESET_ALL}, Size: {len(cobject.response.data)}]'))
            elif cobject.response.status // 100 == 4:
                tqdm.write(' {:<100}{:>20}'.format(cobject.response.payload,
                                                   f' [Status: {Fore.YELLOW}{cobject.response.status}{Style.RESET_ALL}, Size: {len(cobject.response.data)}]'))
    except:
        return


def validate_file(stop_on_success):
    """ Callback used for checking files' content. """

    def validate(future):
        try:
            cobject = future.result()
            if cobject.state == Failed:
                return
            if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
                data = cobject.response.data.decode()
                file = cobject.response.file

            if re.match(dotdotfarm.generators.words_generator.FILES_REGEXP[file], data) == None:
                cobject.state = Failed
                # future.remove_done_callback(add_file(None))
                future.cancel()
            elif stop_on_success:
                for task in asyncio.all_tasks(asyncio.get_event_loop()):
                    task.cancel()
            else:
                pass
        except:
            return

    return validate


def add_file(files_dict):
    """ Callback used for saving data from response. """
# @container(files_dict)
    def add(future):
        try:
            cobject = future.result()
            # if cobject.state == Failed:
            if future.cancelled():
                return cobject
            if type(cobject.response) == dotdotfarm.engines.http_engine.HttpResponse:
                data = cobject.response.data.decode()
            if data not in files_dict.values():
                files_dict[cobject.response.url] = data
        except:
            return

    return add


def exec():
    pass
