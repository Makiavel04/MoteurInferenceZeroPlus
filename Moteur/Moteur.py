#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

def lireFichierJson(filename : str) :
    """
    Lire un fichier .json contenant base de faits et de règles

    :param filename: nom du fichier à lire
    :return: base de faits et de règles extraites du fichier
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    base_faits : dict = data["faits"]
    base_regles : dict = {r["id"] : {k : v for k,v in r.items() if k!="id"} for r in data["règles"]}# Redécoupe le dico en mettant l'id en cle général
    return base_faits, base_regles

###--- CHAINAGE AVANT ---###
def regles_utilisables_chainage_avant(base_regles : dict, base_faits :dict):
    """
    Liste les règles utilisables pour un tour de chaînage avant

    :param base_regles: la base de règles
    :param base_faits: la base de faits
    :return: liste de règles
    """
    regles_eligibles = []
    for id, regle in base_regles.items() :#Parcours de toutes les règles;
        eligible = True
        for fait, val in regle.get("conditions").items() : #Pour chaque fait en prémisse d'une règle, on vérifie si ce fait a la même valeur dans la base de faits.
            if base_faits.get(fait) != val : eligible = False
        if eligible : regles_eligibles.append(id) #Si tous les prémisses d'une règle sont vérifiés, on ajoute cette règle à celles éligibles.

    return regles_eligibles

def chainage_avant_largeur(base_regles : dict, base_faits :dict):
    """
    Résolution par chaînage avant en largeur
    
    :param base_regles: la base de règles
    :param base_faits: la base de faits
    :return: 
    """
    bf = base_faits
    br = base_regles
    regles_eligibles = regles_utilisables_chainage_avant(br, bf)


    while br and regles_eligibles: #tant qu'il reste des règles à appliquer
        #tri des règles
        for regle in regles_eligibles:
            #appliquer regle et mettre à jour la base de fait
            for fait, val in br.get(regle).get("conclusion").items() :
                bf[fait] = val### à l'ajout de conséquence dans base de fait, on peut verif si existe deja et transformer en liste de val ou planter

            #retirer les règles utilisées
            del br[regle]

        regles_eligibles = regles_utilisables_chainage_avant(br, bf)

    return bf


if __name__ == "__main__":
    print("moteur")

    base_faits, base_regles = lireFichierJson("../FichiersTest/test1.json")

    #print("LOG :",base_regles)

    #Chaînage avant en largeur
    print(chainage_avant_largeur(base_regles, base_faits))


