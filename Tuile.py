#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
from enum import Enum


class Symbol(Enum):
	Sun = 0
	Moon = 1


class Tuile:
	
	def __init__(self, symbol=Symbol.Moon, bonus=0, up=-1, left=-1, right=-1):
		self.symbol = symbol
		self.bonus = bonus
		self.directions = [up, left, right]
