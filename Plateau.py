#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tuile import *
from Colonne import *
from Candidats import *
from Bonus import *
from SunMoon import *
import bisect


class CombiATester:
	def __init__(self, combi, dispos, colonne_relaxee, score):
		self.combi = combi
		self.dispos = dispos
		self.colonne_relaxee = colonne_relaxee
		self.score = score
		
	def __lt__(self, other):
		if self.score != other.score:
			return self.score < other.score
		return self.combi < other.combi
		
		
# Plateau de jeu
class Plateau:
	
	def __init__(self, id, tuiles, places_tuiles, places_tuiles_up, conversion_score):
		self.id = id
		self.tuiles = tuiles  # L'ensemble des tuiles existantes
		self.places_tuiles = places_tuiles  # Ordre de placement des tuiles dans l'algo de remplissage selon l'indice de colonne et de ligne de chaque direction
		self.places_tuiles_up = places_tuiles_up
		self.conversion_score = conversion_score
		self.candidats = Candidats(tuiles)
		lignes = [4, 5, 6, 7, 6, 5, 4]
		self.directions = [[Colonne(i, lignes[i], dir, self.candidats) for i in range(len(lignes))] for dir in range(3)]  # Représentation des tuiles du plateau selon chaque direction (haut, gauche, droite)
		self.tuiles_restantes = [i for i in range(len(tuiles))]  # Indices des tuiles non posées
		self.ensemble_bonus = EnsembleBonus(tuiles, self)
		self.sun_moon = SunMoon(self)
		self.tuiles_posees = []
		self.score = 0
		
		self.colonnes = [[], [], []]
		self.cols_non_remplies_score_nul = [[], [], []]
		self.combi = [[], [], []]
		self.vides = [[], [], []]
		self.scores_col = [[], [], []]
		self.dispos_generales = []
		self.dispos_par_col = []
		self.all_val_possible = []
		self.col_impactees = []
		self.max_score_possible = 0
		
	def __lt__(self, other):
		if self.score != other.score:
			return self.score < other.score
		if len(self.tuiles_posees) != len(other.tuiles_posees):
			return len(self.tuiles_posees) < len(other.tuiles_posees)
		return self.id > other.id
	
	def recopie(self, other):
		self.candidats.recopie(other.candidats)
		for dir in range(3):
			for col in range(len(other.directions[dir])):
				self.directions[dir][col].recopie(other.directions[dir][col])
		self.tuiles_restantes = [id for id in other.tuiles_restantes]  # Indices des tuiles non posées
		self.ensemble_bonus.recopie(other.ensemble_bonus)
		self.sun_moon.recopie(other.sun_moon)
		self.tuiles_posees = [id for id in other.tuiles_posees]
		
	# Ajoute une tuile à la position libre suivante, si possible
	def poser_tuile(self, indice_tuile):
		coord = self.places_tuiles[len(self.tuiles_posees)]  # Colonnes dans les 3 systèmes de coordonnées
		tuile = self.tuiles[indice_tuile]
		self.tuiles_posees.append(indice_tuile)
		self.candidats.poser_tuile(tuile)
		for dir in range(3):
			for col in range(len(self.directions[dir])):
				self.directions[dir][col].poser_tuile(tuile, coord[dir][0] == col, coord[dir][1])
		self.ensemble_bonus.poser_tuile(tuile, coord)
		self.sun_moon.poser_tuile()
		self.tuiles_restantes.remove(indice_tuile)
	
	# Méthode pour afficher un nombre toujours de même taille
	@staticmethod
	def __to_str(num):
		if num == -1 or num > 9:
			return str(num)
		return str(num) + " "
	
	# Affichage du plateau
	def __str__(self):
		# Construction d'une structure facile à afficher
		ups = [[None] * ligne for ligne in [4, 5, 6, 7, 6, 5, 4]]
		for i in range(len(self.tuiles_posees)):
			ups[self.places_tuiles_up[i][0]][self.places_tuiles_up[i][1]] = self.tuiles[self.tuiles_posees[i]]
		retour = ""
		for ligne in range(7):  # Rq : autant de lignes max que de colonnes
			for colonne in ups:
				if len(colonne) > ligne:
					if colonne[ligne] is not None:
						retour += "   " + self.__to_str(self.conversion_score[0][colonne[ligne].directions[0]]) + "   "
					else:
						retour += "   " + self.__to_str(-1) + "   "
				else:
					retour += "        "
			retour += "\n"  # Nouvelle ligne
			for colonne in ups:
				if len(colonne) > ligne:
					if colonne[ligne] is not None:
						retour += " " + self.__to_str(self.conversion_score[1][colonne[ligne].directions[1]]) + "  "
						retour += self.__to_str(self.conversion_score[2][colonne[ligne].directions[2]]) + " "
					else:
						retour += " " + self.__to_str(-1) + "  " + self.__to_str(-1) + " "
				else:
					retour += "        "
			retour += "\n" * 2
		return retour
	
	# Evaluation du plateau
	def evalue(self):
		self.dispos_generales = [[self.candidats.nb_vals[dir][i] for i in range(4)] for dir in range(3)]
		score_dir = [0, 0, 0]
		for dir in range(3):
			for indice_col in [0, 6, 1, 5, 2, 4, 3]: # Trier de la plus petite à la plus grande, pour relaxer les contraintes en premier sur les petites colonnes
				col = self.directions[dir][indice_col]
				if col.score_max == 0 and len(col.tuiles) != 0:
					self.cols_non_remplies_score_nul[dir].append(col)
				elif col.score_max != 0 and len(col.tuiles) < len(col):
					self.colonnes[dir].append(col)
					self.vides[dir].append(len(col) - len(col.tuiles))
					if len(col.tuiles) != 0:
						self.combi[dir].append(1)  # 2e valeur = tout sauf la bonne valeur
						indice = col.tuiles[0].directions[dir]
						self.scores_col[dir].append([0, self.conversion_score[dir][indice] * len(col)])
						score_dir[dir] += self.scores_col[dir][-1][1]
					else:
						self.combi[dir].append(4)  # 5e valeur = tout et n'importe quoi
						self.scores_col[dir].append([0, 0, 0, 0, 0])
						for j in range(0, 4):
							self.scores_col[dir][-1][j + 1] = self.conversion_score[dir][j] * len(col)
						score_dir[dir] += self.scores_col[dir][-1][4]
						indice = 3
					self.dispos_generales[dir][indice] -= self.vides[dir][-1]
				elif len(col.tuiles) == len(col) and col.score_max != 0:
					self.score += self.conversion_score[dir][col.tuiles[0].directions[dir]] * len(col)
					
		if len(self.tuiles_posees) < 4:
			self.score += self.__evalue_dir(score_dir)
		else:
			self.__init_all_val_possible()
			self.col_impactees = self.__init_col_impactees(self.colonnes, self.colonnes)
			self.__init_dispos_par_colonne()
			self.__evalue_all_dirs(0, score_dir[0] + score_dir[1] + score_dir[2], 0)
			self.score += self.max_score_possible
		self.score += self.ensemble_bonus.score_max + self.sun_moon.score_max * 10
		
	def __evalue_dir(self, score_dir):
		score_tot = 0
		for dir in range(3):
			# Calcul du meilleur score en mettant en compétition toutes les colonnes non nulles non complètes
			if self.__combi_possible(self.dispos_generales[dir]):
				score_tot += score_dir[dir]
			else:
				self.max_score_possible = 0
				self.__evaluer_combi(0, dir, score_dir[dir])
				score_tot += self.max_score_possible
		return score_tot

	# Première combinaison
	def __init_combi(self, colonnes):
		combi = []
		for c in colonnes:
			if len(c.tuiles) != 0:
				combi.append(1)  # 2e valeur = tout sauf la bonne valeur
			else:
				combi.append(4)  # 5e valeur = tout et n'importe quoi
		return combi
	
	def __init_dispos_par_colonne(self):
		# Rq : on ne fait pas le min entre les dispos générale est ça puisque de toute façon on vérifie séparément les dispos générales
		old_dirs = [1, 0, 0]  # Left to right  # Up to right # Up to left
		new_dirs = [2, 2, 1]  # Left to right  # Up to right # Up to left
		for dir in new_dirs:
			self.dispos_par_col.append([])
			for id_col in range(len(self.colonnes[dir])):
				if len(self.colonnes[dir][id_col].tuiles) != 0:
					self.dispos_par_col[-1].append([-self.vides[dir][id_col]])
				else:
					self.dispos_par_col[-1].append([0, 0, 0, -self.vides[dir][id_col]])
		
		for id_col in range(len(self.combi[0])):
			for i in self.col_impactees[1][id_col]:
				for val in self.all_val_possible[1][id_col][i][self.combi[0][id_col]]:
					self.dispos_par_col[1][i][val] += 1
			for i in self.col_impactees[2][id_col]:
				for val in self.all_val_possible[2][id_col][i][self.combi[0][id_col]]:
					self.dispos_par_col[2][i][val] += 1
		for id_col in range(len(self.combi[1])):
			for i in self.col_impactees[0][id_col]:
				for val in self.all_val_possible[0][id_col][i][self.combi[1][id_col]]:
					self.dispos_par_col[0][i][val] += 1
	
		#  Ne pas oublier les colonnes non pleines avec un score nul
		col_impactees_joker = self.__init_col_impactees(self.cols_non_remplies_score_nul, self.colonnes)
		for indice_impact in range(3):
			for id_col_modifiee in range(len(self.cols_non_remplies_score_nul[old_dirs[indice_impact]])):
				for id_col_impactee in col_impactees_joker[indice_impact][id_col_modifiee]:
					for val in self.dispos_par_col[indice_impact][id_col_impactee]:
						val += 1

	def __get_val_combi(self, dir, id_col):
		if len(self.colonnes[dir][id_col].tuiles) != 0:
			return self.colonnes[dir][id_col].tuiles[0].directions[dir]
		return self.combi[dir][id_col] - 1

	def __combi_possible(self, dispos):
		for d in dispos:
			if d < 0:
				return False
		return True
	
	def __combi_possible2(self, dir):
		if dir != 0:
			if dir == 1:
				for disp in self.dispos_par_col[2]:
					for d in disp:
						if d < 0:
							return False
			else:
				for disp in self.dispos_par_col[0]:
					for d in disp:
						if d < 0:
							return False
				for disp in self.dispos_par_col[1]:
					for d in disp:
						if d < 0:
							return False
		return True
	
	def __score_combi(self, combi, scores_col):
		score = 0
		for i in range(len(combi)):
			score += scores_col[i][combi[i]]
		return score
	
	def __evaluer_combi(self, colonne_relaxee, dir, score):
		# On essaie des combinaisons moins contraignantes (en évitant de tester plusieurs fois la même combi)
		c = self.combi[dir]
		d = self.dispos_generales[dir]
		v = self.vides[dir]
		cols = self.colonnes[dir]
		sc = self.scores_col[dir]
		for i in range(colonne_relaxee, len(c)):
			if c[i] > 0:  # On ne peut pas relaxer plus
				score2 = score + sc[i][c[i] - 1] - sc[i][c[i]]
				if score2 > self.max_score_possible:
					if len(cols[i].tuiles) != 0:
						old_val = cols[i].tuiles[0].directions[dir]
					else:
						old_val = c[i] - 1
					c[i] -= 1
					d[old_val] += v[i]
					if c[i] > 0:
						d[c[i] - 1] -= v[i]
					if self.__combi_possible(d):
						self.max_score_possible = score2
					else:
						self.__evaluer_combi(i, dir, score2)  # Récursif
					if c[i] > 0:
						d[c[i] - 1] += v[i]
					d[old_val] -= v[i]
					c[i] += 1
	
	def __evalue_all_dirs(self, dir, score, colonne_relaxee):
		dg = self.dispos_generales[dir]
		if self.__combi_possible(dg) and self.__combi_possible2(dir):
			if dir != 2:
				self.__evalue_all_dirs(dir + 1, score, 0)
			else:
				self.max_score_possible = max(score, self.max_score_possible)
		else:
			# On essaie des combinaisons moins contraignantes (en évitant de tester plusieurs fois la même combi)
			c = self.combi[dir]
			sc = self.scores_col[dir]
			v = self.vides[dir]
			cols = self.colonnes[dir]
			for i in range(colonne_relaxee, len(c)):
				if c[i] > 0:  # On ne peut pas relaxer plus
					score2 = score + sc[i][c[i] - 1] - sc[i][c[i]]
					if dir != 2 or score2 > self.max_score_possible:
						if len(cols[i].tuiles) != 0:
							old_val = cols[i].tuiles[0].directions[dir]
						else:
							old_val = c[i] - 1
						c[i] -= 1
						dg[old_val] += v[i]
						if c[i] > 0:
							dg[c[i] - 1] -= v[i]
						self.__update_dispos_par_col_combi(dir, i, c[i] + 1, c[i])
						self.__evalue_all_dirs(dir, score2, i)
						self.__update_dispos_par_col_combi(dir, i, c[i], c[i] + 1)
						if c[i] > 0:
							dg[c[i] - 1] += v[i]
						dg[old_val] -= v[i]
						c[i] += 1
	
	def __update_dispos_par_col_combi(self, dir, id_col, old_combi, new_combi):
		if dir == 0:
			self.__update_dispos_par_col_combi_val(1, id_col, old_combi, new_combi)
			self.__update_dispos_par_col_combi_val(2, id_col, old_combi, new_combi)
		elif dir == 1:
			if old_combi > 0:
				self.dispos_par_col[2][id_col][old_combi - 1] += self.vides[dir][id_col]
			if new_combi > 0:
				self.dispos_par_col[2][id_col][new_combi - 1] -= self.vides[dir][id_col]
			self.__update_dispos_par_col_combi_val(0, id_col, old_combi, new_combi)
		else:
			if old_combi > 0:
				self.dispos_par_col[0][id_col][old_combi - 1] += self.vides[dir][id_col]
				self.dispos_par_col[1][id_col][old_combi - 1] += self.vides[dir][id_col]
			if new_combi > 0:
				self.dispos_par_col[0][id_col][new_combi - 1] -= self.vides[dir][id_col]
				self.dispos_par_col[1][id_col][new_combi - 1] -= self.vides[dir][id_col]
			
	def __init_col_impactees(self, cols_modifiees, cols_impactees):
		base = [
			[[i for i in range(max(0, col.id - 3), min(6, col.id + 3) + 1)] for col in cols_modifiees[1]],  # Left to right
			 [[i for i in range(max(0, 3 - col.id), min(6, 9 - col.id) + 1)] for col in cols_modifiees[0]],  # Up to right
			 [[i for i in range(max(0, col.id - 3), min(6, col.id + 3) + 1)] for col in cols_modifiees[0]]]  # Up to left
		exceptions = [
			[[min(6, col.id + 3) - indice_ligne for indice_ligne in col.positions_tuiles_placees] for col in cols_modifiees[1]],  # Left to right
			[[max(0, 3 - col.id) + indice_ligne for indice_ligne in col.positions_tuiles_placees] for col in cols_modifiees[0]],  # Up to right
			[[max(0, col.id - 3) + indice_ligne for indice_ligne in col.positions_tuiles_placees] for col in cols_modifiees[0]]]  # Up to left
		
		new_col_1 = dict()
		for i in range(len(cols_impactees[1])):
			new_col_1[cols_impactees[1][i].id] = i
		new_col_2 = dict()
		for i in range(len(cols_impactees[2])):
			new_col_2[cols_impactees[2][i].id] = i
		new_col = [new_col_2, new_col_2, new_col_1]
		
		return [[[new_col[j][i] for i in base[j][col] if i not in exceptions[j][col] and i in new_col[j]] for col in range(len(exceptions[j]))] for j in range(3)]
		
	def __init_val_possible(self, old_dir, new_dir):
		old_cols = self.colonnes[old_dir]
		val_possible = []
		for i in range(len(old_cols)):
			val_possible.append([])
			if len(old_cols[i].tuiles) != 0:
				old_val = old_cols[i].tuiles[0].directions[old_dir]
				for new_col in self.colonnes[new_dir]:
					val_possible[-1].append([])
					if len(new_col.tuiles) != 0:
						new_val = new_col.tuiles[0].directions[new_dir]
						val_possible[-1][-1].append({0})
						val_possible[-1][-1].append(set([0 for id in self.tuiles_restantes if self.tuiles[id].directions[old_dir] == old_val and self.tuiles[id].directions[new_dir] == new_val]))
					else:
						val_possible[-1][-1].append({0, 1, 2, 3})
						val_possible[-1][-1].append(set([self.tuiles[id].directions[new_dir] for id in self.tuiles_restantes if self.tuiles[id].directions[old_dir] == old_val]))
			else:
				for new_col in self.colonnes[new_dir]:
					val_possible[-1].append([])
					if len(new_col.tuiles) != 0:
						new_val = new_col.tuiles[0].directions[new_dir]
						val_possible[-1][-1].append({0})
						for old_val in range(0, 4):
							val_possible[-1][-1].append(set([0 for id in self.tuiles_restantes if self.tuiles[id].directions[old_dir] == old_val and self.tuiles[id].directions[new_dir] == new_val]))
					else:
						val_possible[-1][-1].append({0, 1, 2, 3})
						for old_val in range(0, 4):
							val_possible[-1][-1].append(set([self.tuiles[id].directions[new_dir] for id in self.tuiles_restantes if self.tuiles[id].directions[old_dir] == old_val]))
		return val_possible
		
	def __init_all_val_possible(self):
		self.all_val_possible = [
			self.__init_val_possible(1, 2),  # Left to right
			self.__init_val_possible(0, 2),  # Up to right
			self.__init_val_possible(0, 1),  # Up to left
		]
	
	def __update_dispos_par_col_combi_val(self, indice_impact, indice_col, old_combi, new_combi):
		for i in self.col_impactees[indice_impact][indice_col]:
			for val in self.all_val_possible[indice_impact][indice_col][i][old_combi]:
				self.dispos_par_col[indice_impact][i][val] -= 1
			for val in self.all_val_possible[indice_impact][indice_col][i][new_combi]:
				self.dispos_par_col[indice_impact][i][val] += 1
				