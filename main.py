"Can"#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
from Plateau import *
import bisect


def init_tuiles():
    retour = [
        Tuile(Symbol.Moon, 0, 0, 2, 1),
        Tuile(Symbol.Sun, 0, 0, 1, 3),
        Tuile(Symbol.Sun, 0, 0, 2, 2),
        Tuile(Symbol.Moon, 0, 0, 1, 2),
        Tuile(Symbol.Moon, 0, 0, 3, 0),
        Tuile(Symbol.Sun, 0, 0, 3, 1),
        Tuile(Symbol.Sun, 0, 1, 2, 1),
        Tuile(Symbol.Moon, 0, 1, 0, 2),
        Tuile(Symbol.Moon, 0, 1, 3, 1),
        Tuile(Symbol.Sun, 0, 1, 2, 3),
        Tuile(Symbol.Sun, 0, 1, 3, 2),
        Tuile(Symbol.Moon, 0, 1, 2, 0),
        Tuile(Symbol.Moon, 0, 2, 0, 3),
        Tuile(Symbol.Moon, 0, 2, 2, 1),
        Tuile(Symbol.Sun, 0, 0, 0, 2),
        Tuile(Symbol.Sun, 0, 2, 0, 2),
        Tuile(Symbol.Sun, 0, 2, 2, 2),
        Tuile(Symbol.Moon, 0, 0, 0, 3),
        Tuile(Symbol.Moon, 0, 2, 3, 2),
        Tuile(Symbol.Sun, 0, 2, 2, 0),
        Tuile(Symbol.Sun, 0, 3, 0, 3),
        Tuile(Symbol.Sun, 0, 3, 1, 2),
        Tuile(Symbol.Sun, 0, 3, 2, 1),
        Tuile(Symbol.Moon, 0, 3, 0, 2),
        Tuile(Symbol.Moon, 0, 3, 2, 2),
        Tuile(Symbol.Sun, 0, 0, 2, 0),
        Tuile(Symbol.Sun, 0, 3, 2, 3),
        
        Tuile(Symbol.Moon, 40, 0, 1, 0),
        Tuile(Symbol.Sun, 40, 1, 0, 1),
        Tuile(Symbol.Moon, 0, 3, 3, 1),
        Tuile(Symbol.Sun, 0, 2, 3, 3),
        Tuile(Symbol.Moon, 0, 3, 0, 0),
        Tuile(Symbol.Moon, 0, 2, 2, 3),
        Tuile(Symbol.Sun, 0, 1, 1, 2),
        Tuile(Symbol.Moon, 0, 0, 2, 3),
        Tuile(Symbol.Moon, 0, 3, 1, 1),
        Tuile(Symbol.Moon, 40, 1, 0, 0),
        Tuile(Symbol.Sun, 0, 2, 3, 1),
        Tuile(Symbol.Moon, 0, 1, 3, 3),
        Tuile(Symbol.Sun, 0, 3, 3, 2),
        Tuile(Symbol.Sun, 0, 2, 1, 3),
        Tuile(Symbol.Sun, 0, 3, 0, 1),
        Tuile(Symbol.Sun, 40, 1, 1, 0),
        Tuile(Symbol.Moon, 0, 3, 2, 0),
        Tuile(Symbol.Moon, 40, 0, 0, 1),
        Tuile(Symbol.Moon, 0, 1, 1, 3),
        Tuile(Symbol.Moon, 0, 2, 1, 2),
        Tuile(Symbol.Moon, 0, 2, 3, 0),
        Tuile(Symbol.Sun, 80, 0, 0, 0),
        Tuile(Symbol.Sun, 0, 3, 3, 0),
        Tuile(Symbol.Moon, 0, 2, 0, 1),
        Tuile(Symbol.Moon, 0, 3, 3, 3),
        Tuile(Symbol.Moon, 0, 1, 2, 2),
        Tuile(Symbol.Sun, 0, 1, 0, 3),
        Tuile(Symbol.Moon, 0, 0, 3, 2),
        Tuile(Symbol.Sun, 40, 0, 1, 1),
        Tuile(Symbol.Sun, 0, 1, 3, 0),
        Tuile(Symbol.Moon, 80, 1, 1, 1),
        Tuile(Symbol.Moon, 0, 2, 1, 0),
        Tuile(Symbol.Sun, 0, 2, 1, 1),
        Tuile(Symbol.Sun, 0, 2, 0, 0),
        Tuile(Symbol.Sun, 0, 0, 3, 3),
        Tuile(Symbol.Sun, 0, 3, 1, 0),
        Tuile(Symbol.Moon, 0, 3, 1, 3),
        
        # Tuile(Symbol.Moon, 0, 0, 2, 1),
        # Tuile(Symbol.Sun, 0, 0, 1, 3),
        # Tuile(Symbol.Sun, 0, 0, 2, 2),
        # Tuile(Symbol.Moon, 0, 0, 1, 2),
        # Tuile(Symbol.Moon, 0, 0, 3, 0),
        # Tuile(Symbol.Sun, 0, 0, 3, 1),
        # Tuile(Symbol.Sun, 0, 1, 2, 1),
        # Tuile(Symbol.Moon, 0, 1, 0, 2),
        # Tuile(Symbol.Moon, 0, 1, 3, 1),
        # Tuile(Symbol.Sun, 0, 1, 2, 3),
        # Tuile(Symbol.Sun, 0, 1, 3, 2),
        # Tuile(Symbol.Moon, 0, 1, 2, 0),
        # Tuile(Symbol.Moon, 0, 2, 0, 3),
        # Tuile(Symbol.Moon, 0, 2, 2, 1),
        # Tuile(Symbol.Sun, 0, 0, 0, 2),
        # Tuile(Symbol.Sun, 0, 2, 0, 2),
        # Tuile(Symbol.Sun, 0, 2, 2, 2),
        # Tuile(Symbol.Moon, 0, 0, 0, 3),
        # Tuile(Symbol.Moon, 0, 2, 3, 2),
        # Tuile(Symbol.Sun, 0, 2, 2, 0),
        # Tuile(Symbol.Sun, 0, 3, 0, 3),
        # Tuile(Symbol.Sun, 0, 3, 1, 2),
        # Tuile(Symbol.Sun, 0, 3, 2, 1),
        # Tuile(Symbol.Moon, 0, 3, 0, 2),
        # Tuile(Symbol.Moon, 0, 3, 2, 2),
        # Tuile(Symbol.Sun, 0, 0, 2, 0),
        # Tuile(Symbol.Sun, 0, 3, 2, 3)
    ]
    
    # retour.sort()
    # random.shuffle(retour)
    
    vrai_retour = []
    for i in range(37):
        vrai_retour.append(retour[i])
    return vrai_retour


# Conversion des coordonnées de la vision "up" en ceux de la vision "left"
def up_to_left(coord):
    col = max(0, coord[0] - 3) + coord[1]
    lig = coord[0] - max(0, max(0, coord[0] - 3) + coord[1] - 3)
    return [col, lig]


# Conversion des coordonnées de la vision "up" en ceux de la vision "right"
def up_to_right(coord):
    col = coord[1] + max(0, 3 - coord[0])
    if coord[1] >= 3 or coord[0] >= 3:
        lig = coord[0] + min(0, coord[1] - 3)
        return [col, lig]
    lig = min(coord[1], coord[0])
    return [col, lig]
    
def init_places_tuiles():
    # Ordre de placement des tuiles dans l'algo de remplissage selon chaque système de coordonnées (haut, gauche, droite)
    places_up = [
        [3, 3], [4, 0], [6, 2], [1, 4], [2, 0], [5, 4], [0, 2], [3, 6], [6, 0], [0, 0], [5, 2], [4, 4], [2, 4], [1, 2],
        [2, 1], [4, 1], [6, 3], [3, 0], [0, 3], [1, 3], [5, 3], [3, 1], [6, 1], [1, 0], [2, 5], [4, 5], [5, 0], [0, 1],
        [3, 5], [5, 1], [1, 1], [2, 2], [2, 3], [3, 4], [4, 3], [4, 2], [3, 2]
    ]
    
    return places_up, [[place, up_to_left(place), up_to_right(place)] for place in places_up]


# Construction des tuiles du jeu
tuiles = init_tuiles()

# Détermination d'un ordre de remplissage des cases du plateau
places_tuiles_up, places_tuiles = init_places_tuiles()

conversion_score = [[1, 4, 9, 12], [2, 6, 7, 11], [3, 5, 8, 10]]

score_mini = 600  # Aide au départ
indice_plateau = 0
candidats = [Plateau(indice_plateau, tuiles, places_tuiles, places_tuiles_up, conversion_score)]
candidats[-1].evalue()
indice_plateau += 1

# Test des fils
while len(candidats) != 0:
    
    candidat = candidats.pop()
    
    # Debug
    print("Candidat : ", end='')
    for id in candidat.tuiles_posees:
        print(str(id) + " ", end='')
    print("Nb candidats : " + str(len(candidats)) + " Score potentiel : " + str(candidat.score))

    # si on a tout rempli
    if len(candidat.tuiles_posees) == 37:
        # On a trouvé le meilleur score
        print("Score :" + str(candidat.score))
        print(str(candidat))
        break
    
    for indice_tuile in candidat.tuiles_restantes:
        
        # Copie
        plateau = Plateau(indice_plateau, tuiles, places_tuiles, places_tuiles_up, conversion_score)
        plateau.recopie(candidat)
        indice_plateau += 1

        # Poser une tuile et évaluer le plateau
        plateau.poser_tuile(indice_tuile)
        plateau.evalue()
        
        # Debug
        # if len(plateau.tuiles_posees) == 6 and indice_tuile == 5:
        #     print("New : ", end='')
        #     for id in plateau.tuiles_posees:
        #         print(str(id) + " ", end='')
        #     print("Nb candidats : " + str(len(candidats)) + " Score potentiel : " + str(plateau.score))
        #     input("plop")

        if plateau.score > score_mini:
            bisect.insort(candidats, plateau)
    
    
