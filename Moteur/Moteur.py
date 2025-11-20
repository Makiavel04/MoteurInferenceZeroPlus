#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import json
from collections import OrderedDict



def lire_fichier_json(filename : str) :
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


###--- TRIE DES REGLES ---###
"""def trier_regles(base_regles: dict, base_faits: dict, type_tri: str):
    Trie les règles et renvoie un dictionnaire trié, même structure que base_regles.

    # Convertir les règles en liste pour les trier
    regles_liste = [
        {"id": rid, 
         "conditions": r["conditions"], 
         "conclusion": r["conclusion"]}
        for rid, r in base_regles.items()
    ]

    # ----------------------------- TRI 1 : Plus de prémisses -----------------------------
    if type_tri == "0":
        regles_liste.sort(key=lambda r: len(r["conditions"]), reverse=True)

    # ----------------------------- TRI 2 : Faits récents -----------------------------
    elif type_tri == "1":
        faits_ordonnes = list(base_faits.items())
        index_fait = {(k, v): i for i, (k, v) in enumerate(faits_ordonnes)}

        def priorite(regle):
            indices = [
                index_fait[(fait, val)]
                for fait, val in regle["conditions"].items()
                if (fait, val) in index_fait
            ]
            return max(indices) if indices else -1

        regles_liste.sort(key=priorite, reverse=True)

    else:
        raise ValueError(f"Type de tri inconnu : {type_tri}")

    # ----------------------------- RECONSTRUCTION EN DICTIONNAIRE -----------------------------
    base_regles_triees = OrderedDict()

    for r in regles_liste:
        base_regles_triees[r["id"]] = {
            "conditions": r["conditions"],
            "conclusion": r["conclusion"]
        }

    return base_regles_triees"""

def tri_regles_par_anciennete(liste_regles : list, base_regles : dict, base_faits : dict, recent : bool = True):
    """
    Tri les règles par ancienneté des prémisses

    :param liste_regles:
    :param base_faits:
    :param recent:
    :return:
    """
    #Classe les faits
    index_faits = list(base_faits.items())

    #Vecteur d'ancienneté des règles
    vect_regles = dict()
    for id in liste_regles :
        conditions = base_regles.get(id).get("conditions")
        vect = [index_faits.index((attr, val)) for attr, val in conditions.items()]
        vect.sort(reverse=True)
        vect_regles[id] = vect
    print(vect_regles)
    #Tri par ancienneté
    print(sorted(liste_regles, key= lambda r : vect_regles.get(r), reverse=recent))
    return sorted(liste_regles, key= lambda r : vect_regles.get(r), reverse=recent)


def tri_regles_par_nbpremisses(liste_regles : list, base_regles : dict, decroissant : bool = False):
    """
    Tri des règles selon le nombre de prémisses à satisfaire

    :param liste_regles: regles à trier
    :param base_regles: base de règles
    :param decroissant: trier par nombre de prémisses à satisfaire
    :return: liste de règles triée
    """
    return sorted(liste_regles, key= lambda r: len(base_regles[r]["conditions"]), reverse=decroissant)


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
            if base_faits.get(fait) != val :
                eligible = False
                break
        if eligible : regles_eligibles.append(id) #Si tous les prémisses d'une règle sont vérifiés, on ajoute cette règle à celles éligibles.

    return regles_eligibles

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

        #Tri des règles
        match critere_tri :
            case "aucun" : pass
            case "nbpremisses_croiss" : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, False) #Tri par Nombre de prémisses croissant
            case "nbpremisses_decroiss" : regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles, True) #Tri par Nombre de prémisses décroissant
            case "premisse_rec" : regles_eligibles = tri_regles_par_anciennete(regles_eligibles, base_regles, base_faits, True) #Tri par prémisses les plus récentes
            case "premisse_anc" : regles_eligibles = tri_regles_par_anciennete(regles_eligibles, base_regles, base_faits, False) #-------------------------- anciens
            case _ : raise ValueError("Critère de tri inexistant.")

        if trace:
            print("Tour", tour,
                  "\nRègles applicables :", regles_eligibles,
                  "\nBase de faits courantes :", bf,
                  "\nRègles disponibles :", br)

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



###--- CHAINAGE ARRIERE ---###
def regles_utilisables_car(base_regles : dict, but : dict) :
    """
    Liste les règles utilisables pour un tour de chaînage arrière

    :param base_regles: la base de règles
    :param but: l'objectif à atteindre
    :return: la liste des règles utilisables pour ce tour
    """
    # regles_eligibles = []
    # for id, regle in base_regles.items():  # Parcours de toutes les règles;
    #     if regle.get("conclusion").get(but.get("attribut")) == but.get("valeur") :
    #         regles_eligibles.append(id)
    #
    # return regles_eligibles
    return [id for id, regle in base_regles.items() if regle.get("conclusion").get(but.get("attribut")) == but.get("valeur")]


def chainage_arriere(base_regles : dict, base_faits :dict, but : dict, critere_tri :str = "aucun", trace : bool = False) :
    """
    Résolution par chaînage arrière

    :param base_regles: base de règles initiales
    :param base_faits: base de faits
    :param but: objectif à prouver
    :critère de séléction de règle en cas de conflit
    :param trace: activer ou désactiver la trace
    :return: un couple (bool, dict) avec vrai si prouvable et l'arbre de preuve
    """
    arbre = {"but": but, "prouvable": False, "enfants": [], "regle": None}

    if base_faits.get(but.get("attribut")) == but.get("valeur") :
        if trace : print(but.get("attribut"),":",but.get("valeur"),"est dans la base de faits")
        arbre["prouvable"] = True
        return True, arbre

    regles_eligibles = regles_utilisables_car(base_regles, but)
    if not regles_eligibles : #Si pas de règles pour aboutir à ce but et comme déjà verif si dans BF,
        if trace: print(but.get("attribut"), ":", but.get("valeur"), "n'est pas dans la base et n'est en conclusion d'aucune règle")
        return False, arbre #On ne peut pas atteindre ce but
    match critere_tri:
        case "aucun": pass
        case "nbpremisses_croiss": regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles,False)  # Tri par Nombre de prémisses croissant
        case "nbpremisses_decroiss": regles_eligibles = tri_regles_par_nbpremisses(regles_eligibles, base_regles,True)  # Tri par Nombre de prémisses décroissant
        case "premisse_rec": regles_eligibles = tri_regles_par_anciennete(regles_eligibles, base_regles, base_faits, True) #Tri par prémisses les plus récentes
        case "premisse_anc" : regles_eligibles = tri_regles_par_anciennete(regles_eligibles, base_regles, base_faits, False)  # -------------------------- anciens
        case _: raise ValueError("Critère de tri inexistant.")

    for idregle in regles_eligibles :
        #Tri / Critère de résolution de conflits (non def pour l'instant)
        br = copy.deepcopy(base_regles) #Refait une copie à chaque fois pour en supprimer la règle actuelle
        conditions = br.get(idregle).get("conditions")
        del br[idregle]
        enfants = []  # On initialise les enfants pour cet essai de règle seulement

        #Remonté de la règle
        prouvable = True
        for attr, val in conditions.items() :
            etat, enfant = chainage_arriere(br, base_faits, {"attribut" : attr, "valeur" : val}, critere_tri, trace)
            enfants.append(enfant)
            if(etat == False) :#Si une prémisse de la règle n'est pas prouvable, alors la conclusion de la règle ne peut être prouvé avec celle-ci.
                if trace : print(but.get("attribut"), ":", but.get("valeur"),"n'est pas démontrable par",idregle,"car l'antécédent",attr,":",val,"n'est pas obtenable avec les bases de faits et de règles actuels")
                prouvable = False
                break #S'arrête pour cette règle

        if prouvable : #Si toutes les prémisses d'une règle sont prouvables, alors la conclusion l'est aussi
            if trace : print(but.get("attribut"), ":", but.get("valeur"), "est prouvé par la règle",base_regles.get(idregle))
            arbre["prouvable"] = True
            arbre["enfants"] = enfants
            arbre["regle"] = idregle
            return True, arbre

    if trace : print(but.get("attribut"), ":", but.get("valeur"), "n'est prouvable par aucune des règles :",regles_eligibles)
    return False, arbre

def afficher_arbre(arbre, prefix=""):
    """
    Affiche un arbre de chaînage arrière de manière graphique.

    :param arbre: dictionnaire {"but": ..., "prouvable": bool, "enfants": [...]}
    :param prefix: préfixe utilisé pour l'indentation
    """
    but = arbre["but"]
    status = "✔" if arbre["prouvable"] else "✘"
    regle_info = f" [{arbre['regle']}]" if arbre.get("regle") else ""
    print(f"{prefix}- {but['attribut']} = {but['valeur']} {status}{regle_info}")

    enfants = arbre.get("enfants", [])
    for i, enfant in enumerate(enfants):
        if i == len(enfants) - 1:
            new_prefix = prefix + "   └─ "
        else:
            new_prefix = prefix + "   ├─ "
        afficher_arbre(enfant, prefix=new_prefix)
        
        
###--- CHAINAGE PAR PAQUETS ---###

def construire_arbre(base_faits: dict, base_regles: dict):
    """
    Construire un arbre de dépendances entre règles.
    Une règle enfant est liée à un parent si au moins une de ses prémisses
    correspond à une conséquence du parent.
    Seules les règles directement applicables (toutes conditions satisfaites par la base de faits) sont racines.
    """

    def arbre_depuis_regle(reg_id, regles_restantes):
        arbre = {"Règle": reg_id, "Enfants": []}
        consequences_parent = regles_restantes[reg_id]["conclusion"]

        for enfant_id, regle in regles_restantes.items():
            if enfant_id == reg_id:
                continue
            conditions_enfant = regle.get("conditions", {})
            # lien parent -> enfant si au moins une prémisse correspond à une conséquence
            if any(fait in conditions_enfant and conditions_enfant[fait] == val
                   for fait, val in consequences_parent.items()):
                arbre["Enfants"].append(arbre_depuis_regle(enfant_id, regles_restantes))

        return arbre

    # Règles racines : toutes les conditions satisfaites par la base de faits
    racines = [
        reg_id for reg_id, regle in base_regles.items()
        if all(fait in base_faits and base_faits[fait] == val
               for fait, val in regle.get("conditions", {}).items())
    ]

    arbre_racine = {"Règle": None, "Enfants": []}
    for reg_id in racines:
        arbre_racine["Enfants"].append(arbre_depuis_regle(reg_id, base_regles))

    return arbre_racine





def afficher_arbre_regles(arbre, prefix=""):
    """
    Affiche l'arbre des règles de manière hiérarchique.

    :param arbre: dictionnaire {"Règle": id, "Enfants": [...]}
    :param prefix: chaîne pour indentation (utilisée en récursion)
    """
    regle = arbre.get("Règle")
    if regle is None:
        print(f"{prefix}- Racine")
    else:
        print(f"{prefix}- {regle}")

    enfants = arbre.get("Enfants", [])
    for i, enfant in enumerate(enfants):
        # Gestion des branches graphiques ├─ et └─
        if i == len(enfants) - 1:
            new_prefix = prefix + "   └─ "
        else:
            new_prefix = prefix + "   ├─ "
        afficher_arbre_regles(enfant, prefix=new_prefix)

def afficher_base_regles(base_regles: dict):
    """
    Affiche proprement la base de règles sous forme lisible.
    """
    print("\n=== BASE DES RÈGLES ===\n")

    for reg_id, reg in base_regles.items():
        print(f"• {reg_id}")
        print("   Conditions :")

        if reg["conditions"]:
            for fait, valeur in reg["conditions"].items():
                print(f"       - {fait} = {valeur}")
        else:
            print("       (aucune)")

        print("   Conclusion :")
        for fait, valeur in reg["conclusion"].items():
            print(f"       → {fait} = {valeur}")

        print()  # ligne vide entre les règles



def recuperer_predecesseurs(base_regles :dict, trace : bool):
    """
    Créer un graphe de dépendance entre les règles.

    :param base_regles: base de règles
    :param base_faits: base de faits
    :return: ordre des règles
        """
    predecesseurs = dict()
    for id in base_regles.keys() :
        predecesseurs[id] = []

    for id, regle in base_regles.items() : #Parcours de toutes les règles;
        for attr, val in regle.get("conclusion").items() : #Pour chaque fait en conclusion d'une règle
                
            for id2, regle2 in base_regles.items() : #On regarde les autres règles
                if id != id2 and (((attr,val) in regle2.get("conditions").items())): #Si une prémisse d'une règle correspond à une conséquence d'une autre règle
                    predecesseurs[id2].append(id) #On ajoute la règle id au prédecesseur de la règle id
                        
    if trace : print("Prédécesseurs :", predecesseurs)
    return predecesseurs

def creer_ordre(base_regles :dict, base_faits : dict, trace : bool):
    """
    Créer un ordre des règles selon leurs prédécesseurs.

    :param base_regles: base de règles
    :param base_faits: base de faits
    :return: ordre des règles
        """
    predecesseurs = recuperer_predecesseurs(base_regles, trace)

    ordre_regles = []
    
    while predecesseurs : #Tant qu'il reste des règles à ordonner
        #Groupe i récupère les règles dont les predécesseurs sont déjà validés
        groupe = [idr for idr, preds in predecesseurs.items() if (not preds) or all((attr,val) in base_faits.items() for attr, val in base_regles.get(idr).get("conditions").items())]
        ordre_regles.append(groupe)

        if not groupe : raise ValueError("Aucune règle déclenchable : cycle détecté ou faits initiaux insuffisants") ### Voir pour ajouter fonction d'incohérence ou demande à l'expert


        for r in groupe :
            del predecesseurs[r] #On enlève les règles déjà ordonnées
        for id in predecesseurs.keys() :
            predecesseurs[id] = [p for p in predecesseurs[id] if p not in groupe] #On enlève les prédécesseurs déjà ordonnés

    if trace : print("Groupes à appliquer :", ordre_regles, "\n")
    return ordre_regles


def appliquer_regle_pour_groupe(base_regles : dict, base_faits : dict, regle : str, trace : bool):
    """
    Appliquer un règle d'un groupe

    :param base_regles: base des règles
    :param base_faits: base des faits
    :param regle: nom de la règle à appliquer
    :param trace: trace activée ou non
    :return: la base de faits mise à jour
    """
    if trace: print("Ajout des faits par application de", regle, " : ", end="")  # TRACE
    for (attr, val) in base_regles.get(regle).get("conclusion").items():
        base_faits[attr] = val ###Voir pour les multivaluations (chercher dans liste multival et [])
        if trace: print("(", attr, ":", val, "), ", end="") #TRACE
    if trace : print()
    return base_faits

def appliquer_groupe(base_regles : dict, base_faits : dict, groupe : list, trace : bool):
    """
    Appliquer un groupe de règle

    :param base_regles: base des règles
    :param base_faits: base des faits
    :param groupe: groupe de règle à appliquer
    :param trace: trace activée ou non
    :return: la base de faits mise à jour
    """
    if trace : print("Application du groupe :", groupe)
    for r in groupe :
        eligible = True
        for attr, val in base_regles.get(r).get("conditions").items():
            if base_faits.get(attr) != val :
                eligble = False
                break

        if eligible :
            base_faits = appliquer_regle_pour_groupe(base_regles, base_faits, r, trace)

    if trace : print() #Saut de ligne
    return base_faits


def resolution_par_groupes(base_regles : dict, base_faits :dict, but : dict | None, trace : bool = False):
    """

    :param base_regles:
    :param base_faits:
    :param strat:
    :param but:
    :param critere_tri:
    :param trace:
    :return:
    """
    if trace : print("Récap : Résolution par déclenchement de groupes de règles.\n")
    groupes = creer_ordre(base_regles, base_faits, trace)
    for g in groupes :
        base_faits = appliquer_groupe(base_regles, base_faits, g, trace)
        if but != None and base_faits.get(but.get("attribut")) == but.get("valeur") :
            print("Succès : but trouvé")
            return base_faits

    if but != None : print("Échec : but non trouvé")
    return base_faits


###--- MAIN ---###
if __name__ == "__main__":
    try:
        cheminVersFichier = "../FichiersTest/test2.json"#input("Chemin vers le fichier json : ")
        base_regles, base_faits = lire_fichier_json(cheminVersFichier)
        print("LOG :",base_regles, "\n", base_faits)


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
                print("Veuillez donner le nom et la valeur de l'attribut objectif. (Respectez la casse)")
                attr = input("Nom de l'attribut : ")
                val = input("Valeur : ")
                but = {"attribut" : attr, "valeur" : val}

                etat, arbre = chainage_arriere(base_regles, base_faits, but, critere_tri="aucun", trace=trace)
                if etat : print("Succès")
                else : print("Échec")
                afficher_arbre(arbre)

            case "paquets" :
                # Saturation ou objectif
                inputBut = ""
                while inputBut not in ["1", "2"]:
                    inputBut = input("Quel condition d'arrêt voulez-vous utiliser ?\n"
                                     "\t1 - Saturation\n"
                                     "\t2 - Recherche d'un but\n"
                                     "Choix : ")
                match inputBut:
                    case "1":
                        but = None
                    case "2":
                        print("Veuillez donner le nom et la valeur de l'attribut objectif. (Respectez la casse)")
                        attr = input("Nom de l'attribut : ")
                        val = input("Valeur : ")
                        but = {"attribut": attr, "valeur": val}
                    case _:
                        raise ValueError("Condition d'arrêt inconnu.")
                """arbrePaquets = construire_arbre(base_faits, base_regles)
                afficher_arbre_regles(arbrePaquets)
                afficher_base_regles(base_regles)"""
                base_faits = resolution_par_groupes(base_regles, base_faits, but, trace)
    except Exception as e :
        print("Erreur :", e)
