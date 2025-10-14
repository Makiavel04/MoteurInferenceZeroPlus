#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from sympy.strategies.core import switch


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

def tri_regles_par_nbpremisses(liste_regles : list, base_regles : dict, decroissant : bool = False):
    """
    Tri des règles selon le nombre de prémisses à satisfaire

    :param liste_regles: regles à trier
    :param base_regles: base de règles
    :param decroissant: trier par nombre de prémisses à satisfaire
    :return: liste de règles triée
    """
    return sorted(liste_regles, key= lambda r: len(base_regles[r]["conditions"]), reverse=decroissant)

def chainage_avant(base_regles : dict, base_faits :dict, critere_tri :int = 0, trace : bool = False):
    """
    Résolution par chaînage avant en largeur
    
    :param base_regles: la base de règles
    :param base_faits: la base de faits
    :param critere_tri: critère de séléction de règle en cas de conflit
    :param trace: activer ou désactiver la trace
    :return: la base de fait après l'execution
    """
    bf = base_faits
    br = base_regles
    regles_eligibles = regles_utilisables_chainage_avant(br, bf)

    tour = 1

    while br and regles_eligibles: #tant qu'il reste des règles à appliquer

        if trace:
            print("Tour", tour,
                  "\nRègles applicables :", regles_eligibles,
                  "\nBase de faits courantes :", bf,
                  "\nRègles disponibles :", br)

        #tri des règles
        match critere_tri :
            case 1 : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, False) #Tri par Nombre de prémisses croissant
            case 2 : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, True) #Tri par Nombre de prémisses décroissant
            case 3 : pass #Tri par prémisses les plus récentes
            case 4 : pass #-------------------------- anciens
            case _ : pass


        for regle in regles_eligibles:
            if trace : print("Ajout des faits par application de", regle," : ", end="")

            #appliquer regle et mettre à jour la base de fait
            for fait, val in br.get(regle).get("conclusion").items() :
                bf[fait] = val### à l'ajout de conséquence dans base de fait, on peut verif si existe deja et transformer en liste de val ou planter
                if trace : print("(",fait,":", val, "), ", end="")

            #retirer les règles utilisées
            del br[regle]
            if trace : print()#retour à la ligne
            #if profondeur break

        regles_eligibles = regles_utilisables_chainage_avant(br, bf)

        tour +=1
        if trace : print()#retour à la ligne

    return bf


if __name__ == "__main__":
    cheminVersFichier = input("Chemin vers le fichier json : ")
    base_faits, base_regles = lireFichierJson("../FichiersTest/test_plusieursreglepartour.json")
    #print("LOG :",base_regles)

    inputTrace = input("Souhaitez-vous activer la trace ? [y/n] ")
    match inputTrace:
        case "n" :
            trace = False
            print("Trace désactivée")
        case _ :
            trace = True
            print("Trace activée")

    inputTypeRecherche = input("""Quel type de recherche souhaitez-vous utiliser ?
    1 - Chaînage avant
    2 - Chaînage arrière
    3 - Par groupement de règles
    Choix : """)


    match int(inputTypeRecherche) :
        case 1 :#Chaînage avant

            ###Saturation ou objectif

            #Choix type chaînage avant
            inputTypeCA = input("""Quel type de chaînage avant souhaitez-vous utiliser ?
                1 - En largeur
                2 - En profondeur
                Choix : """)
            try:
                typeCA = int(inputTypeCA)
            except ValueError:
                print("Err : valeur par défaut -> En largeur")
                typeCA = 1

            #Choix du critère de résolution de conflit
            inputCritere = input("""Quel critère souhaitez-vous appliquer pour la résolution de conflit dans le choix de la règle à explorer ?
                0 - Aucun (utilise l'ordre des règles dans la base de faits)
                1 - Nombre de prémisses croissant
                2 - Nombre de prémisses décroissant
                3 - Comportant les prémisses les plus récentes
                4 - Comportant les prémisses les plus anciennes
                Choix : """)
            try:
                critere = int(inputCritere)
            except ValueError:
                print("Err : valeur par défaut -> Aucun")
                critere = 0
            print(chainage_avant(base_regles, base_faits, critere_tri = int(critere), trace = trace))

        case 2 :
            #Chaînage arrière
            print("Not implemented : chainage arrière")

        case 3 :
            #Chaînage arrière
            print("Not implemented : chainage arrière")

        case _ :
            print("Non reconnu.")

