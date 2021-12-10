from Plateau import *


class SunMoon:
	def __init__(self, plateau):
		self.score_max = 7
		self.plateau = plateau
	
	def recopie(self, other):
		self.score_max = other.score_max
	
	def poser_tuile(self):
		
		# Mise à jour du score
		if self.score_max != 0:
			for colonne in [3, 4, 2, 5, 1, 6, 0]:
				for direction in self.plateau.directions:
					if len(direction[colonne]) <= self.score_max:
						if direction[colonne].existe_sun or direction[colonne].existe_moon:
							self.score_max = len(direction[colonne])
							return
					else:
						break
			self.score_max = 0
	
