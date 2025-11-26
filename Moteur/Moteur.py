#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import json
from itertools import product


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

def ajout_fait(base_faits : dict, attr: str, val : str):
    """
    Ajout d'un fait à la base. Lève une erreur si le fait y est déjà

    :param base_faits: base de faits
    :param attr: attribut à ajouter
    :param val: valeur de l'attribut
    :return: base de faits mise à jour
    """
    if attr in base_faits.keys() and base_faits.get(attr) != val:
            raise ValueError(f"ajout_fait : Ajout de {attr}={val} à la base de faits, alors qu'il y déjà {attr}={base_faits.get(val)}.")
    else :
        base_faits[attr] = val

    return base_faits


###--- TRIE DES REGLES ---###
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
        ajout_fait(base_faits, fait, val)
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

    while br and regles_eligibles and ((but is None) or (bf.get(but.get("attribut")) != but.get("valeur"))): #tant qu'il reste des règles à appliquer ou si on a atteint l'objectif

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
        ajout_fait(base_faits, attr, val)
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
                eligible = False
                break

        if eligible :
            base_faits = appliquer_regle_pour_groupe(base_regles, base_faits, r, trace)

    if trace : print() #Saut de ligne
    return base_faits


def resolution_par_groupes(base_regles : dict, base_faits :dict, but : dict | None, trace : bool = False):
    """
    Résolution de l'objectif par application de groupe de règles

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


###--- INCOHÉRENCE ---###
def trouver_incoherence_regles(base_regles : dict, trace : bool = False):
    """
    Recherche d'incohérence entre les règles.

    :param base_regles: base de règles
    :param trace: trace activée / désactivée
    :return: présence ou non d'incohérence
    """
    ###Incohérence des règles
    print("INCOHÉRENCE DE RÈGLES :")
    # --- Identifier les faits demandables ---
    attr_premisses = set()
    attr_conclusions = set()
    for (idr, regle) in base_regles.items() :
        attr_premisses.update(regle.get("conditions").keys()) #Tous les attributs en conditions qui ne sont pas déjà dans le set y sont ajoutés
        attr_conclusions.update(regle.get("conclusion").keys())
    demandables = attr_premisses - attr_conclusions
    if trace: print("Attributs demandables :", demandables)

    # --- Identifier les règles dont toutes les prémisses sont demandables ---
    regles_demandables = set()
    for (idr, regle) in base_regles.items():
        if all(attr in demandables for attr in regle.get("conditions").keys()): #Récupère toutes les règles qui n'ont que des attributs demandables en prémisse.
            regles_demandables.add(idr)
    if trace: print("Règles initiales à considérer :", regles_demandables)

    # --- Propagation et indexation ---
    index_derivation = {attr : dict() for attr in attr_conclusions}#Index de tous les attributs non demandables
    for idr, regle in base_regles.items() :
        for attr, val in regle.get("conclusion").items(): #Pour chaque attribut, on définit un dico avec les valeurs possibles
            index_derivation[attr][val] = [] #Pour chaque valeur on prévoit une liste avec ses dérivations.
    #Dico avec chaque attr et un sous dico de valeur qui contient toutes les dérivations
    regles_explorees = []

    while regles_demandables :
        r = regles_demandables.pop()
        if trace : print("Exploration de", r)

        #Calcul de la dérivation de la règle
        premisses_r = base_regles.get(r).get("conditions")
        derivations = [dict()]
        for attr_p, val_p in premisses_r.items():
            if index_derivation.get(attr_p) : # Si l'élément est un élément qui a été dérivé, on récupère ses dérivations
                new_deriv = []
                for d in index_derivation.get(attr_p).get(val_p): #Pour chaque dérivation possible de l'attribut
                    for d2 in derivations : #On l'ajoute aux dérivations existantes
                        tmp = copy.deepcopy(d2)
                        for a, v in d.items() :
                            tmp[a] = v
                        new_deriv.append(tmp)
                derivations = copy.deepcopy(new_deriv)

            else :# Sinon c'est un élément demandable et on le met tel quel
                for i in range(0, len(derivations)):
                    derivations[i][attr_p] = val_p

        conclusion_r = base_regles.get(r).get("conclusion")
        for attr_c, val_c in conclusion_r.items():

            index_derivation.get(attr_c).get(val_c).extend(derivations) #Ajoute la dérivation de la règle à tous les (attribut, valeur) en conclusion

        regles_explorees.append(r)


        #Vérification de la saturation
        for attr in index_derivation.keys() :
            regle_avec_attr = []
            for idr, regle in base_regles.items() :
                if attr in regle.get("conclusion").keys() : regle_avec_attr.append(idr)#Récupère toutes les règles concluant sur un attribut.

            if not(attr in demandables) and all(r in regles_explorees for r in regle_avec_attr) :
                demandables.add(attr)
                if trace : print("Attribut saturé :", attr)


        #Ajout des règles qui sont maintenant utilisables
        for idr, regle in base_regles.items() :
            if not(idr in regles_explorees) and all(attr in demandables for attr in regle.get("conditions").keys()): #Récupère toutes les règles qui n'ont que des attributs demandables en prémisse.
                regles_demandables.add(idr)
                if trace : print("Règle ajoutée :", idr)

        if trace :
            print("Demandables :", demandables)
            print("Règles demandables :", regles_demandables)
            print("Règles explorées :", regles_explorees)
            print()

    if trace :
        print("Index des dérivations :",index_derivation,"\n")

    #Études des incohérences
    incoherent = False
    for attr, val_dict in index_derivation.items() :
        if len(val_dict) > 1 : #Si on a plus de 1 valeur possible pour l'attribut, cela peut entrainer un problème de multivaluation
            valeurs = list(val_dict.keys()) #Récupère les valeurs possibles
            for i in range(0, len(valeurs)):
                v1 = valeurs[i] #Récupère une valeur
                liste_deriv1 = val_dict[v1] #et la liste des dérivations associées
                for j in range(i+1, len(valeurs)):
                    v2 = valeurs[j]
                    liste_deriv2 = val_dict[v2]

                    for (d1, d2) in product(liste_deriv1, liste_deriv2):#teste toutes les combinaisons de dérivations

                        d1_in_d2 = True
                        for k in d1.keys():
                            if not(k in d2.keys()) or d1.get(k) != d2.get(k):
                                d1_in_d2 = False
                                break

                        d2_in_d1 = True
                        for k in d2.keys():
                            if not (k in d1.keys()) or d2.get(k) != d1.get(k):
                                d2_in_d1 = False
                                break

                        if d1_in_d2 or d2_in_d1 :
                            incoherent = True
                            print(f"ATTENTION : {d1} et {d2} concluent sur des valeurs différentes pour un même attribut => {attr}={v1} et {attr}={v2} est INCOHÉRENT")

    if not incoherent : print("RAS\n")
    return incoherent

def trouver_incoherence_faits(base_regles : dict, base_faits: dict, trace : bool = False):
    """
    Vérifier la cohérence des faits en accord avec les règles.
    Pour cela, nous utilisons des méthodes de chaînage avant en profondeur et en saturation, pour pouvoir tester la base de fait après chaque règle.

    :param base_regles: base de règles
    :param base_faits: base de faits
    :param trace: trace activée / désactivée
    :return: présence ou non d'incohérence
    """
    ###Incohérence des faits
    print("INCOHÉRENCE DE FAITS :")

    #Verifier la cohérence des faits après application de chaque règle
    br = copy.deepcopy(base_regles)
    bf = copy.deepcopy(base_faits)

    regles_eligibles = regles_utilisables_cav(br, bf)
    while br and regles_eligibles :
        incoherent = verifier_coherence_fait(br, bf, regles_eligibles[0], trace)#Verifier si la règle éligible que nous utilisons, ici la 1ere
        if incoherent : return True
        appliquer_regle_cav(regles_eligibles[0], br, bf, False) #Revient à faire un tour en profondeur
        regles_eligibles = regles_utilisables_cav(br, bf)

    print("RAS\n")
    return False

def verifier_coherence_fait(base_regles : dict, base_faits : dict, idregle : str, trace : bool = False):
    """
    Vérifier si une règle est cohérente avec la base de faits existante

    :param base_regles: base de règles
    :param base_faits: base de faits
    :param idregle: id de la règle avec laquelle on vérifie
    :param trace: trace activée / désactivée
    :return: présence ou non d'incohérence
    """
    incoherent = False
    for attr, val in base_regles.get(idregle).get("conclusion").items():
        if (attr in base_faits.keys()) and (base_faits.get(attr)!=val):
            print("Attribut en base:", attr, "=", base_faits.get(attr), end=". ")
            print("La règle", idregle, "ajoute :", attr,"=",val+".", "Cela est incohérent.")
            incoherent = True #Si un fait en conclusion de la règle est déjà en base de faits avec une valeur différente, on invalide
    return incoherent

###--- MAIN ---###
if __name__ == "__main__":
    try:
        cheminVersFichier = input("Chemin vers le fichier json : ")
        base_regles, base_faits = lire_fichier_json(cheminVersFichier)
        print("LOG :",base_regles, "\n", base_faits)

        inputTrace = ""
        while inputTrace not in ["y", "n"]:
            inputTrace = input("Souhaitez-vous activer la trace ? [y/n] ")
        match inputTrace:
            case "n" :
                trace = False
                print("Trace désactivée\n")
            case "y" :
                trace = True
                print("Trace activée\n")

        inco_regles = trouver_incoherence_regles(base_regles, trace)
        inco_faits = trouver_incoherence_faits(base_regles, base_faits, trace)


        if inco_faits:
            raise ValueError("FAITS : Incohérence dans la base de faits. Erreur fatal.")
        if inco_regles:
            print("Il y a une incohérence dans la base de règles selon certains faits demandables. (Voir section INCOHÉRENCE RÈGLES)")
            inputIncoRegle = ""
            while inputIncoRegle not in ["y", "n"]:
                inputIncoRegle = input("Si vous êtes sur que cela ne perturbe pas votre execution, car vous n'avez pas ces valeurs, vous pouvez continuer si vous voulez : [y/n]")

            match inputIncoRegle :
                case "y" : pass
                case "n" : raise ValueError("RÈGLES : Arrêt demandé car incohérence de règle")



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
