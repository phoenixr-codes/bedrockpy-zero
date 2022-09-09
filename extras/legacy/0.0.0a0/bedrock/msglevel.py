#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum

class Level(Enum):
    DEBUG = 0
    INFO = 1
    MESSAGE = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5
    NONE = 6