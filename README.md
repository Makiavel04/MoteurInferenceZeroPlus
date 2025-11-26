# Moteur d'inférence - Moteur.py

**Auteurs :** Alexandre Carval, Tristan Cottron

Le programme "Moteur.py" est un moteur d'inférence qui utilise des modèles au format .json pour s'exécuter. Vous pourrez trouver des exemples de .json dans "./FichierTest/".

---

## Format du JSON

Le fichier "exemple.json" montre le format attendu :

```json
{
  "faits" : {
    "attribut1" : "val1",
    "attribut2" : "val2"
  },

  "règles" : [
    {
      "id" :  "R1",
      "conditions" : {
        "attribut1": "val1",
        "attribut2": "val2"
      },
      "conclusion" : {
        "attribut3": "val3"
      }
    }
  ]
}
```

---

## Instructions

1. Lors du lancement du moteur, l'opérateur doit indiquer le chemin vers le fichier qui servira de modèle. (ex : ./FichierTest/exemple.json)

2. Le fichier est ensuite lu pour récupérer la base de fait dans l'attribut "faits" du json et la base de règles dans l'attribut "règles"

3. Le choix est ensuite laissé à l'opérateur d'activer ou non la trace, qui donne des indications détaillées.

4. Viens ensuite les vérifications d'incohérences :
   * Si votre moteur possède une incohérence sur la base de faits, l'exécution sera automatiquement bloquée.
   * Si une incohérence est détectée dans les règles, on laisse le choix à l'opérateur de continuer s'il juge que la base de faits initial ne menace pas l'exécution.

5. L'opérateur peut ensuite choisir une stratégie de recherche parmi les suivantes :
   * Chaînage avant
     * en profondeur : parcours des règles en retriant les règles possibles à chaque tour
     * en largeur : parcours des règles en appliquant toutes les règles possibles à un rang n
   * Chaînage arrière : remonté de règles selon un attribut objectif en conclusion.
   * Déclenchement par groupe de règles : définition de groupes de règles selon les prémisses présentes en conclusion d'autres règles.

6. Pour les chaînages avant et arrière, l'opérateur peut aussi choisir un critère de résolution des conflits, parmi :
   * l'ordre par défaut dans la base de règles
   * la règle ayant le plus ou le moins de prémisses
   * la règle ayant la prémisse la plus ancienne ou la plus récente (chaînage avant uniquement, pas de sens pour le chaînage arrière)

7. Pour le chaînage avant et le déclenchement par groupe, l'opérateur peut soit :

   * exécuter jusqu'à saturation
   * exécuter jusqu'à trouver un attribut avec une valeur précise
