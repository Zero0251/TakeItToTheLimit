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
		self.tuiles_posees = [id for id in other.tuiles_posees]  # Debug
		self.score = other.score
		
		# for col in range(len(self.directions[0])):
		# 	print(str(len(self.directions[0][col])) + "-" + str(len(self.directions[0][col].tuiles)))
		# 	assert ((len(self.directions[0][col].tuiles)) == len(other.directions[0][col].tuiles))
		
	# Ajoute une tuile à la position libre suivante, si possible
	def poser_tuile(self, indice_tuile):
		coord = self.places_tuiles[len(self.tuiles_posees)]  # Colonnes dans les 3 systèmes de coordonnées
		tuile = self.tuiles[indice_tuile]
		self.tuiles_posees.append(indice_tuile) # Debug
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
		self.score = 0
		colonnes = [[], [], []]
		cols_non_remplies_score_nul = [[], [], []]
		for dir in range(3):
			for indice_col in [0, 6, 1, 5, 2, 4, 3]: # Trier de la plus petite à la plus grande, pour relaxer les contraintes en premier sur les petites colonnes
				col = self.directions[dir][indice_col]
				if col.score_max == 0 and len(col.tuiles) != 0:
					cols_non_remplies_score_nul[dir].append(col)
				elif col.score_max != 0 and len(col.tuiles) < len(col):
					colonnes[dir].append(col)
				elif len(col.tuiles) == len(col) and col.score_max != 0:
					self.score += self.conversion_score[dir][col.tuiles[0].directions[dir]] * len(col)
					
		if len(self.tuiles_posees) < 6:
			for dir in range(3):
				self.score += self.__evalue_dir(dir, colonnes[dir])
		else:
			scores_col = []
			vides = []
			dispos_generales =[]
			for dir in range(3):
				scores_col.append(self.__init_scor_col(dir, self.directions[dir]))
				vides.append([len(self.directions[dir][i]) - len(self.directions[dir][i].tuiles) for i in range(7)])
				dispos_generales.append([self.candidats.nb_vals[dir][i] for i in range(4)])
			self.score += self.__evalue_all_dirs([], [], 0, 0, 0, scores_col, vides, dispos_generales, cols_non_remplies_score_nul)
		self.score += self.ensemble_bonus.score_max + self.sun_moon.score_max * 10
		
	def __evalue_dir(self, dir, colonnes):
		# Calcul du meilleur score en mettant en compétition toutes les colonnes non nulles non complètes
		vides = [len(colonnes[i]) - len(colonnes[i].tuiles) for i in range(len(colonnes))]
		scores_col = self.__init_scor_col(dir, colonnes)
		
		# Solution 1
		combi = self.__init_combi(colonnes)
		dispos = self.__init_dispos(dir, combi, colonnes, vides)
		score = self.__score_combi(combi, scores_col)
		if self.__combi_possible(dispos):
			return score
		return self.__evaluer_combi(combi, dispos, 0, 0, score, vides, scores_col, colonnes, dir)
		
		# Solution 3
		# combi = [0] * len(colonnes)
		# for i in range(len(colonnes)):
		# 	if len(colonnes[i].tuiles) != 0:
		# 		combi[i] = - colonnes[i].tuiles[0].directions[dir] - 1
		# self.score += self.__evaluer_combi3(combi, 0, self.candidats.nb_vals[dir][0], 1, [self.candidats.nb_vals[dir][i] for i in range(1, 4)], 0)
		
		# Solution 5
		# indices = [[], [], [], []]  # Ordonnée par valeur
		# for i in range(len(colonnes)):
		# 	if len(colonnes[i].tuiles) != 0:
		# 		indices[colonnes[i].tuiles[0].directions[dir]].append(i)
		# 	else:
		# 		for j in range(4):
		# 			indices[j].append(i)
		# self.dispos = [self.candidats.nb_vals[dir][i] for i in range(4)]
		# self.score += self.__evaluer_combi5(indices, self.candidats.nb_vals[dir][0], 0, 1)
	
	# Première combinaison
	def __init_combi(self, colonnes):
		combi = []
		for c in colonnes:
			if len(c.tuiles) != 0:
				combi.append(1)  # 2e valeur = tout sauf la bonne valeur
			else:
				combi.append(4)  # 5e valeur = tout et n'importe quoi
		return combi
	
	# Vecteur des dispos
	def __init_dispos(self, dir, combi, colonnes, vides):
		dispos = [self.candidats.nb_vals[dir][i] for i in range(4)]
		for i in range(len(combi)):
			if len(colonnes[i].tuiles) != 0:
				dispos[colonnes[i].tuiles[0].directions[dir]] -= vides[i]
			else:
				dispos[combi[i] - 1] -= vides[i]
		return dispos
	
	def __init_dispos_par_dir(self, dir, combi, colonnes, vides):
		dispos = [[0] * 4 for _ in colonnes[dir]]
		for i in range(len(combi[dir])):
			if combi[dir] == 1:
				dispos[i][colonnes[dir][i].tuiles[0].directions[dir]] -= vides[dir][i]
			else:
				dispos[i][3] -= vides[dir][i]
		return dispos
	
	def __init_dispos2(self, dir, colonnes, combi, dispos):
		if dir < 3:
			for i in range(4):
				for j in range(len(colonnes[dir])):
					dispos[dir][j][i] -= self.candidats.nb_vals[dir][i]
		else:
			dict_dispos = dict()
			for col in colonnes[dir]:
				dict_dispos[col.id] = [0, 0, 0, 0]
			for i in range(len(combi[dir - 1])):
				# Quelles valeurs possibles ?
				valeurs_possibles = set([self.tuiles[id].directions[dir] for id in self.tuiles_restantes if self.tuiles[id].directions[dir -1] == i])
				indice_col = colonnes[dir - 1][i].id  # En vrai, on est sur quelle colonne ?
				# Quel impact sur la direction 'dir' ?
				debut_col_impactees = max(0, indice_col - 3)
				fin_col_impactees = min(6, indice_col + 3) + 1
				for j in range(debut_col_impactees, fin_col_impactees):
					if j in dict_dispos:
						for val in valeurs_possibles:
							dict_dispos[j][val] += 1
			for i in range(len(colonnes[dir])):
				dispos[dir][i] += dict_dispos[colonnes[dir][i].id]
			# Debug
			# for i in range(4):
			# 	print("Col : " + str(col.id) + " : val " + str(i) + " : " + str(min(len(col), self.candidats.nb_vals[dir][i])) + " VS " + str(d[i]))
			# print("Pour rappel, les dispos des valeurs sont : ", end='')
			# for i in self.candidats.nb_vals[dir]:
			# 	print(str(i) + " ", end='')
			# print("")
		
	def __init_dispos_par_colonne(self, dir, old_combi, old_colonnes, cols_non_remplies_score_nul):
		if dir == 0:
			return [[self.candidats.nb_vals[dir][j] for j in range(4)] for _ in range(7)]
		if dir == 1:
			#Rq : on ne fait pas le min entre les dispos générale est ça puisque de toute façon on vérifie séparément les dispos générales
			return self.__init_dispos_par_colonne_suite(dir, -1, old_combi[0], old_colonnes[0], cols_non_remplies_score_nul)
		dispos1 = self.__init_dispos_par_colonne_suite(dir, -1, old_combi[1], old_colonnes[1], cols_non_remplies_score_nul)
		dispos2 = self.__init_dispos_par_colonne_suite(dir, -2, old_combi[0], old_colonnes[0], cols_non_remplies_score_nul)
		return [[min(dispos1[i][j], dispos2[i][j]) for j in range(4)] for i in range(7)]
	
	def __init_dispos_par_colonne_suite(self, dir, delta, old_combi, old_colonnes, cols_non_remplies_score_nul):
		# TODO Prendre en compte la position des tuiles déjà placées
		dispos = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
		for i in range(len(old_combi)):
			# Quelles valeurs possibles ?
			if old_combi[i] == 0:
				valeurs_possibles = (0, 1, 2, 3)
			elif old_combi[i] == 1 and len(old_colonnes[i].tuiles) != 0:
				val = old_colonnes[i].tuiles[0].directions[dir + delta]
				valeurs_possibles = set([self.tuiles[id].directions[dir] for id in self.tuiles_restantes if self.tuiles[id].directions[dir + delta] == val])
			else:
				assert (len(old_colonnes[i].tuiles) == 0)
				valeurs_possibles = set([self.tuiles[id].directions[dir] for id in self.tuiles_restantes if self.tuiles[id].directions[dir + delta] == old_combi[i] - 1])
			indice_col = old_colonnes[i].id  # En vrai, on est sur quelle colonne ?
			# Quel impact sur la direction 'dir' ?
			exceptions = []
			if dir == 1:  # Up to left
				debut_col_impactees = max(0, indice_col - 3)
				fin_col_impactees = min(6, indice_col + 3) + 1
				# if i == 2:# TODO Thomas
				for indice_ligne in old_colonnes[i].positions_tuiles_placees: # TODO Thomas
					exceptions.append(max(0, indice_col - 3) + indice_ligne)
					# print("Exceptions pour l'ancienne colonne " + str(old_colonnes[i].id) + " sur la direction 1: ")
					# print(exceptions)
			elif delta == -2:  # Up to right
				debut_col_impactees = max(0, 3 - indice_col)
				fin_col_impactees = min(6, 9 - indice_col) + 1
				for indice_ligne in old_colonnes[i].positions_tuiles_placees: # TODO Thomas
					exceptions.append(max(0, 3 - indice_col) + indice_ligne)
			else:  # Left to right
				debut_col_impactees = max(0, indice_col - 3)
				fin_col_impactees = min(6, indice_col + 3) + 1
				# for indice_ligne in old_colonnes[i].positions_tuiles_placees: # TODO Thomas
				# 	exceptions.append(min(6, indice_col + 3) - indice_ligne)
			for j in range(debut_col_impactees, fin_col_impactees):
				if j not in exceptions:
					for val in valeurs_possibles:
						dispos[j][val] += 1
		# Ne pas oublier les colonnes à score nul non valorisées par la combi
		for col in cols_non_remplies_score_nul[dir + delta]:
			indice_col = col.id
			# Quel impact sur la direction 'dir' ?
			exceptions = []
			if dir == 1:  # Up to left
				debut_col_impactees = max(0, indice_col - 3)
				fin_col_impactees = min(6, indice_col + 3) + 1
				for indice_ligne in col.positions_tuiles_placees:
					exceptions.append(max(0, indice_col - 3) + indice_ligne)
			elif delta == -2:  # Up to right
				assert (dir == 2)
				debut_col_impactees = max(0, 3 - indice_col)
				fin_col_impactees = min(6, 9 - indice_col) + 1
				for indice_ligne in col.positions_tuiles_placees:
					exceptions.append(max(0, 3 - indice_col) + indice_ligne)
			else:  # Left to right
				assert (dir == 2 and delta == -1)
				debut_col_impactees = max(0, indice_col - 3)
				fin_col_impactees = min(6, indice_col + 3) + 1
				for indice_ligne in col.positions_tuiles_placees:
					exceptions.append(min(6, indice_col + 3) - indice_ligne)
			for j in range(debut_col_impactees, fin_col_impactees):
				if j not in exceptions:
					for val in range(4):
						dispos[j][val] += 1
		# if dir == 1:
		# 	print(self)
		# 	print("Tuiles disponibles : ")
		# 	for t in self.tuiles_restantes:
		# 		print(str(self.tuiles[t].directions[0]) + " " + str(self.tuiles[t].directions[1]) + " " + str(self.tuiles[t].directions[2]))
		# 	print("Dispos générales : " + str(self.candidats.nb_vals[dir]))
		# 	print("old combi : " + str(old_combi))
		# 	print("Ce qui donne les dispos par colonnes : ")
		# 	for d in dispos:
		# 		print(d)
		return dispos
		
	# Calcul du score pour toutes les configurations
	def __init_scor_col(self, dir, colonnes):
		scores_col = []
		for i in range(len(colonnes)):
			scores_col.append([0])
			for val in range(1, 5):
				if len(colonnes[i].tuiles) != 0:
					indice = colonnes[i].tuiles[0].directions[dir]
					scores_col[-1].append(self.conversion_score[dir][indice] * len(colonnes[i]))
				else:
					scores_col[-1].append(self.conversion_score[dir][val - 1] * len(colonnes[i]))
		return scores_col
	
	# def __combi_possible(self, combi, dir, colonnes):
	def __combi_possible(self, dispos):
		for d in dispos:
			if d < 0:
				return False
		return True
	
	def __combi_possible2(self, dispos):
		for disp in dispos:
			for d in disp:
				if d < 0:
					return False
		return True
	
	def __score_combi(self, combi, scores_col):
		score = 0
		for i in range(len(combi)):
			score += scores_col[i][combi[i]]
		return score
	
	def __evaluer_combi(self, combi, dispos, colonne_relaxee, max_score_possible, score, vides, scores_col, colonnes, dir):
		# On essaie des combinaisons moins contraignantes (en évitant de tester plusieurs fois la même combi)
		for i in range(colonne_relaxee, len(combi)):
			if combi[i] > 0:  # On ne peut pas relaxer plus
				score2 = score + scores_col[i][combi[i] - 1] - scores_col[i][combi[i]]
				if score2 > max_score_possible:
					if len(colonnes[i].tuiles) != 0:
						indice = colonnes[i].tuiles[0].directions[dir]
					else:
						indice = combi[i] - 1
					combi[i] -= 1
					dispos[indice] += vides[i]
					if combi[i] > 0:
						dispos[combi[i] - 1] -= vides[i]
					if self.__combi_possible(dispos):
						max_score_possible = score2
					else:
						max_score_possible = self.__evaluer_combi(combi, dispos, i, max_score_possible, score2, vides, scores_col, colonnes, dir)  # Récursif
					dispos[indice] -= vides[i]
					if combi[i] > 0:
						dispos[combi[i] - 1] += vides[i]
					combi[i] += 1
		return max_score_possible
	
	# def __evaluer_combi2(self, combi, dispos, vides, scores_col):
	# 	combis_a_tester = [CombiATester(combi, dispos, 0, self.__score_combi(combi, scores_col))]
	#
	# 	while len(combis_a_tester) != 0:
	# 		combi = combis_a_tester.pop()
	#
	# 		# Combinaison possible ? C'est la meilleure
	# 		if self.__combi_possible(combi.dispos):
	# 			return combi.score
	# 		# On essaie des combinaisons moins contraignantes (en évitant de tester plusieurs fois la même combi)
	# 		for i in range(combi.colonne_relaxee, len(combi.combi)):
	# 			if combi.combi[i] > 0:  # On ne peut pas relaxer plus
	# 				dispos2 = [d for d in combi.dispos]
	# 				dispos2[combi.combi[i] - 1] += vides[i]
	# 				if combi.combi[i] > 1:
	# 					dispos2[combi.combi[i] - 2] -= vides[i]
	# 				combi2 = [c for c in combi.combi]
	# 				combi2[i] -= 1
	# 				score2 = combi.score + scores_col[i][combi2[i]] - scores_col[i][combi.combi[i]]
	# 				bisect.insort(combis_a_tester, CombiATester(combi2, dispos2, i, score2))
	# 	return 0
		
	# def __evaluer_combi3(self, combi, indice_augmente, restant, val, dispos, score_courant):
	# 	score = 0
	# 	# Exploration des autres combinaisons possibles pour cette valeur
	# 	for col in range(indice_augmente, len(self.vides)):
	# 		if (combi[col] == 0 or combi[col] == - val) and restant - self.vides[col] >= 0:
	# 			combi2 = [c for c in combi]
	# 			combi2[col] = val
	# 			score = max(score, self.__evaluer_combi3(combi2, col + 1, restant - self.vides[col], val, dispos, score_courant + self.scores_col[col][val]))
	# 	# On s'en tient là pour cette valeur. Choix des valeurs pour les autres colonnes
	# 	if val < 4:
	# 		return max(score, self.__evaluer_combi3(combi, 0, dispos[val - 1], val + 1, dispos, score_courant))
	# 	return max(score, score_courant)  # Toutes les valeurs ont été choisies

	# def __evaluer_combi4(self, combi, indice_augmente, restant, score_courant, val):
	# 	score = 0
	# 	# Exploration des autres combinaisons possibles pour cette valeur
	# 	for col in range(indice_augmente, len(self.vides)):
	# 		if (combi[col] == 0 or combi[col] == - val) and restant - self.vides[col] >= 0:
	# 			combi2 = [c for c in combi]
	# 			combi2[col] = val
	# 			score = max(score, self.__evaluer_combi4(combi2, col + 1, restant - self.vides[col], score_courant + self.scores_col[col][val], val))
	# 	# On s'en tient là pour cette valeur. Choix des valeurs pour les autres colonnes
	# 	for v in range(val + 1, 5):
	# 		for col in range(0, len(self.vides)):
	# 			if (combi[col] == 0 or combi[col] == - v) and self.dispos[v - 1] - self.vides[col] >= 0:
	# 				combi2 = [c for c in combi]
	# 				combi2[col] = v
	# 				score = max(score, self.__evaluer_combi4(combi2, col + 1, self.dispos[v - 1] - self.vides[col], score_courant + self.scores_col[col][v], v))
	# 	return max(score, score_courant)  # Toutes les valeurs ont été choisies
	
	# def __evaluer_combi5(self, indices, restant, score_courant, val):
	# 	score = 0
	# 	# Exploration des autres combinaisons possibles pour cette valeur
	# 	for i in range(len(indices[0])):
	# 		if restant - self.vides[indices[0][i]] >= 0:
	# 			indices2 = [[indices[0][j] for j in range(i + 1, len(indices[0]))]]
	# 			for j in range(1, len(indices)):
	# 				indices2.append([k for k in indices[j] if k != indices[0][i]])
	# 			score = max(score, self.__evaluer_combi5(indices2, restant - self.vides[indices[0][i]], score_courant + self.scores_col[indices[0][i]][val], val))
	# 	# On s'en tient là pour cette valeur. Choix des valeurs pour les autres colonnes
	# 	for v in range(1, len(indices)):
	# 		for i in range(len(indices[v])):
	# 			val2 = val + v
	# 			if self.dispos[val2 - 1] - self.vides[indices[v][i]] >= 0:
	# 				indices2 = [[k for k in indices[j] if k != indices[v][i]] for j in range(v, len(indices))]
	# 				score = max(score, self.__evaluer_combi5(indices2, self.dispos[val2 - 1] - self.vides[indices[v][i]], score_courant + self.scores_col[indices[v][i]][val2], val2))
	# 	return max(score, score_courant)  # Toutes les valeurs ont été choisies
	
	def __evalue_all_dirs(self, old_combi, old_colonne, max_score_possible, score, dir, scores_col, vides, dispos_generales, cols_non_remplies_score_nul):
		dispos_par_col = self.__init_dispos_par_colonne(dir, old_combi, old_colonne, cols_non_remplies_score_nul)
		colonnes = []
		combi = []
		modifs_dispos_generales = [0, 0, 0, 0]  # Trier de la plus petite à la plus grande, pour relaxer les contraintes en premier sur les petites colonnes
		for indice_col in [0, 6, 1, 5, 2, 4, 3]:
			col = self.directions[dir][indice_col]
			vide = vides[dir][indice_col]
			if col.score_max != 0 and vide != 0:
				if len(col.tuiles) != 0:
					val = col.tuiles[0].directions[dir]
					if dispos_par_col[col.id][val] >= vide:
						colonnes.append(col)
						combi.append(1)
						dispos_generales[dir][val] -= vide
						modifs_dispos_generales[val] -= vide
						score += self.conversion_score[dir][val] * len(col)
				else:
					dispo = False
					max_val = 0
					for val in range(4):
						if dispos_par_col[indice_col][val] >= vide:
							dispo = True
							max_val = val
					if dispo:
						colonnes.append(col)
						combi.append(max_val + 1)
						dispos_generales[dir][max_val] -= vide
						modifs_dispos_generales[max_val] -= vide
						score += self.conversion_score[dir][max_val] * len(col)
		max_score_possible = self.__evaluer_combi_all_dirs(combi, dispos_generales, dispos_par_col, 0, max_score_possible, score, vides, scores_col, dir, colonnes, cols_non_remplies_score_nul, old_combi, old_colonne)
		#Annulation
		for i in range(4):
			dispos_generales[dir][i] -= modifs_dispos_generales[i]
		return max_score_possible
	
	def __evaluer_combi_all_dirs(self, combi, dispos_generales, dispos_par_col, colonne_relaxee, max_score_possible, score, vides, scores_col, dir, colonnes, cols_non_remplies_score_nul, old_combi, old_colonne):
		# Debug
		# if dir == 1 and old_combi[0] == [2, 1, 1, 1, 1, 1, 1] and combi == [1, 1, 1, 1, 2, 1, 1]:
		# 	print("Combi " + str(combi) + " possible ?")
		if self.__combi_possible(dispos_generales[dir]) and self.__combi_possible2(dispos_par_col):
			if dir != 2:
				# if dir == 1 and old_combi[0] == [2, 1, 1, 1, 1, 1, 1] and combi == [1, 1, 1, 1, 2, 1, 1]:
				# 	print("Oui")
				old_combi2 = [[j for j in i] for i in old_combi]
				old_combi2.append(combi)
				old_colonne2 = [[j for j in i] for i in old_colonne]
				old_colonne2.append(colonnes)
				return self.__evalue_all_dirs(old_combi2, old_colonne2, max_score_possible, score, dir + 1, scores_col, vides, dispos_generales, cols_non_remplies_score_nul)
			# if score > max_score_possible:
			# 	print("Combinaisons dir 0 meilleure : " + str(old_combi[0]) + " Combi 1 meilleure : " + str(old_combi[1]))
			return max(score, max_score_possible)
		# if dir == 1 and old_combi[0] == [2, 1, 1, 1, 1, 1, 1] and combi == [1, 1, 1, 1, 2, 1, 1]:
		# 	print("Non par ce que : " + str(dispos_generales[dir]) + " ou parce que : ")
		# 	for d in dispos_par_col:
		# 		print(d)
		# On essaie des combinaisons moins contraignantes (en évitant de tester plusieurs fois la même combi)
		for i in range(colonne_relaxee, len(combi)):
			if combi[i] > 0:  # On ne peut pas relaxer plus
				score2 = score + scores_col[dir][colonnes[i].id][combi[i]-1] - scores_col[dir][colonnes[i].id][combi[i]]
				if dir != 2 or score2 > max_score_possible:
					if len(colonnes[i].tuiles) != 0:
						indice = colonnes[i].tuiles[0].directions[dir]
					else:
						indice = combi[i] - 1
					combi[i] -= 1
					dispos_generales[dir][indice] += vides[dir][colonnes[i].id]
					dispos_par_col[colonnes[i].id][indice] += vides[dir][colonnes[i].id]
					if combi[i] > 0:
						dispos_generales[dir][combi[i] - 1] -= vides[dir][colonnes[i].id]
						dispos_par_col[colonnes[i].id][combi[i] - 1] -= vides[dir][colonnes[i].id]
					max_score_possible = self.__evaluer_combi_all_dirs(combi, dispos_generales, dispos_par_col, i, max_score_possible, score2, vides, scores_col, dir, colonnes, cols_non_remplies_score_nul, old_combi, old_colonne)  # Récursif
					dispos_generales[dir][indice] -= vides[dir][colonnes[i].id]
					dispos_par_col[colonnes[i].id][indice] -= vides[dir][colonnes[i].id]
					if combi[i] > 0:
						dispos_generales[dir][combi[i] - 1] += vides[dir][colonnes[i].id]
						dispos_par_col[colonnes[i].id][combi[i] - 1] += vides[dir][colonnes[i].id]
					combi[i] += 1
		return max_score_possible