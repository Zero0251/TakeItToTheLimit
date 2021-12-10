from Tuile import *
from Plateau import *


class Bonus:
	
	def __init__(self, tuile, colonnes, score_max):
		self.colonnes = colonnes
		self.tuile = tuile
		self.score_max = score_max


class EnsembleBonus:
	
	def __init__(self, tuiles, plateau):
		self.score_max = 0
		self.score_init = 0
		self.bonus_poses = []
		self.plateau = plateau
		
		for tuile in tuiles:
			self.score_max += tuile.bonus
			self.score_init += tuile.bonus
	
	def recopie(self, other):
		self.score_max = other.score_max
		self.score_init = other.score_init
		for b in other.bonus_poses:
			self.bonus_poses.append(Bonus(b.tuile, b.colonnes, b.score_max))
	
	def poser_tuile(self, tuile, colonnes):
		# Ajout de la tuile
		if tuile.bonus != 0:
			self.bonus_poses.append(Bonus(tuile, colonnes, tuile.bonus))
			self.score_init -= tuile.bonus
		
		# Mise à jour du score
		if self.score_max != 0:
			new_score_max = self.score_init
			for bonus in self.bonus_poses:
				if bonus.score_max != 0:
					nb_ok = 0
					for dir in range(3):
						if self.plateau.directions[dir][bonus.colonnes[dir][0]].score_max - 1 == bonus.tuile.directions[dir]:
							nb_ok += 1
					if nb_ok == 2:
						bonus.score_max = bonus.tuile.bonus / 2
					elif nb_ok == 3:
						bonus.score_max = bonus.tuile.bonus
					else:
						bonus.score_max = 0
				new_score_max += bonus.score_max
			self.score_max = new_score_max
	
