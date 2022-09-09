#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class DuplicateError(Exception):
    def __init__(self, name):
        super.__init__(f"{name!r} is already registered")
