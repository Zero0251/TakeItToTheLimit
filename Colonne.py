import symbol
from Tuile import *


class Colonne:
	def __init__(self, id, taille, direction, candidats):
		self.id = id
		self.taille = taille
		self.tuiles = []
		self.existe_sun = True
		self.existe_moon = True
		self.score_max = 4
		self.direction = direction
		self.candidats = candidats
		self.positions_tuiles_placees = []
	
	def recopie(self, other):
		self.tuiles = [tuile for tuile in other.tuiles]
		self.existe_sun = other.existe_sun
		self.existe_moon = other.existe_moon
		self.score_max = other.score_max
		self.positions_tuiles_placees = [position for position in other.positions_tuiles_placees]
	
	def __len__(self):
		return self.taille
	
	def poser_tuile(self, tuile, tuile_sur_cette_colonne, position):
		
		if tuile_sur_cette_colonne:
			self.tuiles.append(tuile)
			self.positions_tuiles_placees.append(position)
			if self.existe_sun:
				self.existe_sun = tuile.symbol == Symbol.Sun
			if self.existe_moon:
				self.existe_moon = tuile.symbol == Symbol.Moon
			if self.score_max != 0:
				if len(self.tuiles) == 1:
					if self.candidats.nb_vals[self.direction][tuile.directions[self.direction]] >= self.taille - 1:
						self.score_max = tuile.directions[self.direction] + 1
					else:
						self.score_max = 0
				elif self.score_max != tuile.directions[self.direction] + 1:
					self.score_max = 0
		else:
			if self.existe_sun:
				self.existe_sun = self.candidats.nb_sun >= self.taille - len(self.tuiles)
			if self.existe_moon:
				self.existe_moon = self.candidats.nb_moon >= self.taille - len(self.tuiles)
			if self.score_max != 0:
				if len(self.tuiles) != 0:
					if self.candidats.nb_vals[self.direction][self.score_max - 1] < self.taille - len(self.tuiles):
						self.score_max = 0
				else:
					old_score_max = self.score_max
					self.score_max = 0
					for i in range(old_score_max + 1):
						if self.candidats.nb_vals[self.direction][old_score_max - 1 - i] >= self.taille:
							self.score_max = old_score_max - i
							break
