Auteurs : Alexandre Carval, Tristan Cottron

Le programme "Moteur.py" est un moteur d'inférence qui utilise des modèles au format .json pour s'executer. Vous pourrez trouver des exemples de .json dans "./FichierTest/". Le fichier "exemple.json" montre le format attendu.

Instructions :
1) Lors du lancement du moteur, l'expert doit indiquer le chemin vers le fichier qui servira de modèle.
2) Si votre moteur possède une incohérence sur la base de faits, l'execution sera automatiquement bloquée. Si une incohérence est détectée dans les règles, on laisse le choix à l'opérateur de continuer s'il juge que la base de faits initale ne menace pas l'execution.
3) Si les vérifications se sont bien passées,  on demande alors à l'opérateur de spécifier le type de recherche, et si besoin la stratégie et le critère de résolution des conflits.