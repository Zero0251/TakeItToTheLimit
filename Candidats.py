from Tuile import *


class Candidats:
	
	def __init__(self, tuiles):
		self.nb_vals = [[0 for x in range(4)] for y in range(3)]
		self.nb_sun = 0
		self.nb_moon = 0
		
		for tuile in tuiles:
			if tuile.symbol == Symbol.Sun:
				self.nb_sun += 1
			else:
				self.nb_moon += 1
			for i in range(3):
				self.nb_vals[i][tuile.directions[i]] += 1
	
	def recopie(self, other):
		for y in range(3):
			for x in range(4):
				self.nb_vals[y][x] = other.nb_vals[y][x]
		self.nb_sun = other.nb_sun
		self.nb_moon = other.nb_moon
	
	def poser_tuile(self, tuile):
		if tuile.symbol == Symbol.Sun:
			self.nb_sun -= 1
		else:
			self.nb_moon -= 1
		for i in range(3):
			self.nb_vals[i][tuile.directions[i]] -= 1
	
		
