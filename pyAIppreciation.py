'''
Un script rapide pour générer des appréciations de bulletin à partir de données importées depuis un fichier CSV généré par Pronote. L'API OpenAI est utilisée ici pour générer les appréciations. Ce script est à adapter en fonction des données importées et des appréciations souhaitées !

AVERTISSEMENT : ce script est proposé à titre de démonstration et ne remplace en rien le travail de rédaction d'appréciation du professeur. En effet, la rédaction d'une appréciation de bulletin ne se résume à une simple concaténation de qualificatifs en fonction des notes obtenues par l'élève. Une connaissance poussée du son profil est nécessaire, chose qu'une machine ne peut faire. Ainsi, les appréciations proposées ici ne sont donc pas utilisables en l'état. Enfin, une attention particulière devra être portée à l'anonymisation des données (nom, prénom).
'''

# On importe les modules nécessaires
import csv
import openai
import numpy as np

# On initialise les listes et variables
resultats = ""
nom = []
moyenne = []
notes = []
qualificatifs = []
participations = []
evolutions = []

# On initialise l'API OpenAI avec la clé d'API
# À récupérer sur https://beta.openai.com/account/api-keys après avoir créé un compte
openai.api_key = "sk-..."

# On crée une fonction qui permet de choisir un qualificatif en fonction de la moyenne dans la discipline
def qualificatif(moyenne):
    if moyenne < 10:
        return "insuffisant"
    elif moyenne <= 12:
        return "tout juste satisfaisant"
    elif moyenne <= 14:
        return "satisfaisant"
    elif moyenne <= 16:
        return "très satisfaisant"
    elif moyenne <= 20:
        return "excellent"

# On crée une fonction qui permet de choisir un qualificatif en fonction de la participation dans la discipline
def participation(participation):
    if participation < 10:
        return "comportement inadéquat et participation insuffisante"
    elif participation <= 12:
        return "participation assez satisfaisante"
    elif participation <= 14:
        return "bonne participation"
    elif participation <= 18:
        return "très bonne participation, motrice pour la classe"
    elif participation <= 20:
        return "comportement exemplaire et participation remarquable"

# On crée une fonction qui permet de choisir un qualificatif en fonction de l'évolution des résultats de l'élève
def evolution(evolution):
    # On renverse la liste pour avoir les résultats les plus ancien en premier
    evolution = evolution[::-1]

    # On réalise une modélisation affine à partir de deux listes de valeurs avec la fonction numpy.polyfit et on recupère la pente a
    a = np.polyfit(range(len(evolution)), evolution, 1)[0]

    # On calcule aussi l'écart-type des valeurs de la liste
    ecart_type = np.std(evolution)

    # On choisit un qualificatif en fonction de la pente a et de l'écart-type
    phrase_evolution = "des résultats "
    if a <= -0.5:
        phrase_evolution+="en baisse significative "
    elif -0.5 > a < -0.1:
        phrase_evolution+="en légère baisse "
    elif -0.1 >= a < 0.1:
        phrase_evolution+="constants "
    elif a < 0.5:
        phrase_evolution+="en légère hausse "
    elif a >= 0.5:
        phrase_evolution+="en hausse significative "

    if ecart_type < 1:
        phrase_evolution+="et homogènes"
    elif ecart_type < 2:
        phrase_evolution+="mais variables"
    elif ecart_type >= 3:
        phrase_evolution+="mais irréguliers"

    return phrase_evolution

# On crée une fonction qui permet d'importer les données depuis un fichier CSV et qui les répartit dans les listes, en faisant appel aux fonctions précédentes
def importation():
    # On lit le fichier CSV importé depuis Pronote
    print("Lecture du fichier CSV...")
    with open('data.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # On saute les 2 premières lignes (entêtes avec dates et coefficients dans le cas de Pronote)
        next(csv_reader)
        next(csv_reader)
        
        # On lit les lignes suivantes
        for line in csv_reader:
            # On remplace les virgules par des points
            line = [x.replace(',', '.') for x in line]

            # On remplace les absences par des 0 (à modifier...)
            line = [0 if x == "Abs" else x for x in line]

            # On convertit les notes en flottants
            line = [float(x) if i != 0 else x for i, x in enumerate(line)]

            # On ajoute les données aux listes
            nom.append(line[0])
            moyenne.append(line[1])
            notes.append([line[2:]])
            qualificatifs.append(qualificatif(line[1]))
            # Dans le cas présenté, la note de participation est dans la 3ème colonne
            participations.append(participation(float(line[2]))) 
            # On récupère l'évolution des notes de l'élève depuis le début de l'année (dans le cas présenté, on commence à la 4ème colonne jusqu'à la dernière)
            evolutions.append(evolution(line[3:])) 

# On génère une appréciation pour chaque élève en faisant appel à l'API OpenAI
def appréciations(resultats):
    print("Génération des appréciations...")
    for i in range(len(nom)-1):
        prompt = "Génère une appréciation de bulletin pour l'élève "+nom[i]+" qui a obtenu les résultats suivant en Physique-Chimie au premier trimestre : "+qualificatifs[i]+", "+str(moyenne[i])+" sur 20 de moyenne, "+evolutions[i]+", "+participations[i]+"."
        # print(prompt)

        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.4,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        # On stocke le résultat dans la chaîne de caractères "resultats"
        resultats += response.choices[0].text+"\n"
        # print(response.choices[0].text)

    # On écrit la chaîne de caractères "résultats" dans un fichier txt
    with open('output.txt', 'a') as f:
        f.write(resultats)

    # On ferme le fichier
    f.close()
    print('Appréciations générées avec succès !')

# On lance les fonctions importation() et appréciations()
importation()
appréciations(resultats)