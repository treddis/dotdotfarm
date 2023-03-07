#!/usr/bin/env python3
# ! -*- coding: utf-8 -*-

class CallbackObjectState:
    pass


class Passing(CallbackObjectState):
    pass


class Failed(CallbackObjectState):
    pass


class CallbackObject:
    def __init__(self, response):
        self.state = Passing
        self.response = response
