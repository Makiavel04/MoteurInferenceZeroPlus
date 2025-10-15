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
    f.close()
    base_faits : dict = data["faits"]
    base_regles : dict = {r["id"] : {k : v for k,v in r.items() if k!="id"} for r in data["règles"]}# Redécoupe le dico en mettant l'id en cle général
    return base_regles,base_faits

###--- CHAINAGE AVANT ---###
def regles_utilisables_cav(base_regles : dict, base_faits :dict):
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

def appliquer_regle_cav(regle : dict, base_regles :dict, base_faits : dict, trace : bool):
    """
    Appliquer une règle en chaînage avant

    :param regle: la règle à appliquer
    :param base_regles: la base de règles disponibles
    :param base_faits: la base de faits
    :param trace: activer ou désactiver la trace
    :return: la base de règles et de faits mises à jour
    """
    if trace: print("Ajout des faits par application de", regle, " : ", end="") #TRACE

    # Appliquer la règle et mettre à jour la base de fait
    for fait, val in base_regles.get(regle).get("conclusion").items():
        base_faits[fait] = val  ### à l'ajout de conséquence dans base de fait, on peut verif si existe deja et transformer en liste de val ou planter
        if trace: print("(", fait, ":", val, "), ", end="") #TRACE

    # Retirer la règle utilisée de la base de règles disponibles
    del base_regles[regle]
    if trace: print() #TRACE
    return base_regles, base_faits

def tour_cav_profondeur(regles_eligibles : list, base_regles : dict, base_faits : dict, trace):
    """
    Appliquer un tour de chaînage avant en largeur

    :param regles_eligibles: règles utilisables pour le tour actuel
    :param base_regles: base de règles disponibles
    :param base_faits: base de faits
    :param trace: activer ou désactiver la trace
    :return:
    """
    base_regles, base_faits = appliquer_regle_cav(regles_eligibles[0], base_regles, base_faits, trace)
    return base_regles, base_faits

def tour_cav_largeur(regles_eligibles : list, base_regles : dict, base_faits : dict, trace):
    """
    Appliquer un tour de chaînage avant en profondeur

    :param regles_eligibles: règles utilisables pour le tour actuel
    :param base_regles: base de règles disponibles
    :param base_faits: base de faits
    :param trace: activer ou désactiver la trace
    :return:
    """
    for regle in regles_eligibles:
            base_regles, base_faits = appliquer_regle_cav(regle, base_regles, base_faits, trace)
    return base_regles, base_faits

def chainage_avant(base_regles : dict, base_faits :dict, strat : str, but : dict | None, critere_tri :str = "aucun", trace : bool = False):
    """
    Résolution par chaînage avant
    
    :param base_regles: la base de règles
    :param base_faits: la base de faits
    :param strat: stratégie d'application du chaînage avant
    :param but: but à atteindre
    :param critere_tri: critère de séléction de règle en cas de conflit
    :param trace: activer ou désactiver la trace
    :return: la base de fait après l'execution
    """
    bf = base_faits
    br = base_regles
    regles_eligibles = regles_utilisables_cav(br, bf)

    tour = 1

    print("Récap : \n", "chaînage avant en "+strat+"\n", "critère de résolution des conflits : "+critere_tri+"\n")

    while br and regles_eligibles and (but is None or bf.get(but.get("attribut")) != but.get("valeur")): #tant qu'il reste des règles à appliquer ou si on a atteint l'objectif

        if trace:
            print("Tour", tour,
                  "\nRègles applicables :", regles_eligibles,
                  "\nBase de faits courantes :", bf,
                  "\nRègles disponibles :", br)

        #Tri des règles
        match critere_tri :
            case "aucun" : pass
            case "nbpremisses_croiss" : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, False) #Tri par Nombre de prémisses croissant
            case "nbpremisses_decroiss" : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, True) #Tri par Nombre de prémisses décroissant
            case "premisse_rec" : pass #Tri par prémisses les plus récentes
            case "premisse_anc" : pass #-------------------------- anciens
            case _ : raise ValueError("Critère de tri inexistant.")

        # Réaliser le tour
        match strat :
            case "largeur" : tour_cav_largeur(regles_eligibles, br, bf, trace)
            case "profondeur" : tour_cav_profondeur(regles_eligibles, br, bf, trace)
            case _ : raise ValueError("Type de chaînage avant inexistant.")

        regles_eligibles = regles_utilisables_cav(br, bf)

        tour +=1
        if trace : print()#retour à la ligne

    if but is None : return bf
    else :
        if bf.get(but.get("attribut")) != but.get("valeur") : print("But non atteint")
        else : print("résolu")
        return bf, but



if __name__ == "__main__":
    try:
        #cheminVersFichier = input("Chemin vers le fichier json : ")
        base_regles, base_faits = lireFichierJson("../FichiersTest/test_plusieursreglepartour.json")
        #print("LOG :",base_regles)
        #print(chainage_avant(base_regles, base_faits, 2, critere_tri=1, trace=True))

        inputTrace = ""
        while inputTrace not in ["y", "n"]:
            inputTrace = input("Souhaitez-vous activer la trace ? [y/n] ")
        match inputTrace:
            case "n" :
                trace = False
                print("Trace désactivée")
            case "y" :
                trace = True
                print("Trace activée")
            case _ :
                raise ValueError("Action de trace non reconnu")

        inputTypeRecherche = ""
        while inputTypeRecherche not in ["1","2","3"]:
            inputTypeRecherche = input("Quel type de recherche souhaitez-vous utiliser ?\n"
            "\t1 - Chaînage avant\n"
            "\t2 - Chaînage arrière\n"
            "\t3 - Par groupement de règles\n"
            "Choix : ")

        match inputTypeRecherche :
            case "1" : typeRecherche = "avant"
            case "2" : typeRecherche = "arrière"
            case "3" : typeRecherche = "paquets"
            case _ : raise ValueError("Type de recherche inconnu")

        match typeRecherche :
            case "avant" :#Chaînage avant
                #Saturation ou objectif
                inputBut = ""
                while inputBut not in ["1", "2"] :
                    inputBut = input("Quel condition d'arrêt voulez-vous utiliser ?\n"
                        "\t1 - Saturation\n"
                        "\t2 - Recherche d'un but\n"
                        "Choix : ")
                match inputBut :
                    case "1" : but = None
                    case "2" :
                        print("Veuillez donner le nom et la valeur de l'attribut objectif. (Respectez la casse)")
                        attr = input("Nom de l'attribut : ")
                        val = input("Valeur : ")
                        but = {"attribut" : attr, "valeur" : val}
                    case _ : raise ValueError("Condition d'arrêt inconnu.")

                #Choix type chaînage avant
                inputStratCA = ""
                while inputStratCA not in ["1", "2"] :
                    inputStratCA = input("Quel stratégie de chaînage avant souhaitez-vous utiliser ?\n"
                        "\t1 - En largeur\n"
                        "\t2 - En profondeur\n"
                        "Choix : ")
                match inputStratCA :
                    case "1" : stratCA = "largeur"
                    case "2" : stratCA = "profondeur"
                    case _ : raise ValueError("Stratégie de chaînage avant inconnu")

                #Choix du critère de résolution de conflit
                inputCritere = ""
                while inputCritere not in ["0", "1", "2", "3", "4", "5"]:
                    inputCritere = input("Quel critère souhaitez-vous appliquer pour la résolution de conflit dans le choix de la règle à explorer ?\n"
                    "\t0 - Aucun (utilise l'ordre des règles dans la base de faits)\n"
                    "\t1 - Nombre de prémisses croissant\n"
                    "\t2 - Nombre de prémisses décroissant\n"
                    "\t3 - Comportant les prémisses les plus récentes\n"
                    "\t4 - Comportant les prémisses les plus anciennes\n"
                    "Choix : ")

                match inputCritere :
                    case "0" : critere = "aucun"
                    case "1" : critere = "nbpremisses_croiss"
                    case "2" : critere = "nbpremisses_decroiss"
                    case "3" : critere = "premisse_rec"
                    case "4" : critere = "premisse_anc"
                    case _ : raise ValueError("Critère de résolution de conflit inconnu")

                print(chainage_avant(base_regles, base_faits, stratCA, but, critere_tri = critere, trace = trace))

            case "arrière" :
                #Chaînage arrière
                print("Not implemented : chainage arrière")

            case "paquets" :
                #Chaînage arrière
                print("Not implemented : chainage arrière")

    except Exception as e :
        print("Erreur :", e)

