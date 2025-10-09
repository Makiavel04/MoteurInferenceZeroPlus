#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

def ouvrirFichier(filename : str) :
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_faits : dict = data["faits"]
    base_regles : dict = {r["id"] : {k : v for k,v in r.items() if k!="id"} for r in data["règles"]}# Redécoupe le dico en mettant l'id en cle général
    return base_faits, base_regles

def remplir_pile_ordre_apparition(base_faits :dict, base_regles : dict):
    liste : list = []
    for id,v in base_regles.items():#parcours des règles

        correspond : bool = True
        for attr, val in v["conditions"] :
            if base_faits[attr]!=val:
                correspond = False
                break
        if correspond :
            liste.append(id)

    return liste

def chainage_avant_largeur(base_regles : dict, base_fait : dict): #Par saturation
    sature : bool = False

    while(sature or not(base_regles)): #passer un dico en booleen renvoien True si plein et False sinon
        liste_idregles = remplir_pile_ordre_apparition(base_faits, base_regles)


    return


if __name__ == "__main__":
    print("moteur")

    base_faits, base_regles = ouvrirFichier("../FichiersTest/test1.json")

    #print("LOG :",base_regles)

    #Chaînage avant en largeur



