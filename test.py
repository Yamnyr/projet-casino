import sqlite3
from random import randrange
import time
import threading

# Connexion à la base de données SQLite
try:
    conn = sqlite3.connect('levels6.db')
    print("Connexion à la base de données réussie.")
except Exception as e:
    print(f"Erreur de connexion à la base de données : {e}")

cursor = conn.cursor()

# Création de la table si elle n'existe pas déjà
cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        pseudo TEXT PRIMARY KEY,
        level INTEGER,
        dernier_level INTEGER,
        argent INTEGER
    )
''')
conn.commit()

def enregistrer_score(name, level, dernier_level):
    try:
        cursor.execute("SELECT * FROM utilisateurs WHERE pseudo = ?", (name,))
        result = cursor.fetchone()

        if result:
            ancien_level = result[1]
            # Mettre à jour les deux champs si le nouveau niveau est meilleur
            if level > ancien_level:
                cursor.execute("UPDATE utilisateurs SET level = ?, dernier_level = ? WHERE pseudo = ?",
                               (level, dernier_level, name))
                print(f"Félicitations {name}, votre niveau a été mis à jour à {level} !")
            else:
                cursor.execute("UPDATE utilisateurs SET dernier_level = ? WHERE pseudo = ?",
                               (dernier_level, name))
                print(f"{name}, votre niveau actuel est inférieur à votre meilleur niveau ({ancien_level}).")
        else:
            # Insertion d'un nouvel utilisateur avec le niveau actuel et dernier niveau
            cursor.execute("INSERT INTO utilisateurs (pseudo, level, dernier_level) VALUES (?, ?, ?)",
                           (name, level, dernier_level))
            print(f"Niveau de {name} enregistré à {level}.")

        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du score : {e}")
        

TEMPS_MAX=10       
level = 1
name = input('Je suis Python. Quel est votre pseudo ? \n')
# Récupération du dernier niveau joué (dernier_level) si l'utilisateur existe
cursor.execute("SELECT dernier_level FROM utilisateurs WHERE pseudo = ?", (name,))
result = cursor.fetchone()

if result:
    # Si l'utilisateur existe, on récupère le dernier_level
    dernier_level = result[0]
    level = dernier_level  # On fixe le niveau actuel au dernier joué
    print(f"Re-bienvenue {name} ! Vous recommencez à votre dernier niveau : {level}")
else:
    dernier_level = 1  # Si c'est un nouvel utilisateur, on commence au niveau 1
    enregistrer_score(name, level, dernier_level)

while True:
        
        if level > 3:
            level = int(input(f'{name}, quel niveau voulez vous ? : '))
        if level < 1:
            level=1
        nb_essais = 3 + (2 * level - 2)

        print('--------------------------------------------------------------------------------')
        print(f'Vous êtes au niveau : {level}')

        nb_ordi = randrange(1, level * 10 + 1)

        print(f'\t- Je viens de penser à un nombre entre 1 et {level * 10}. Devinez lequel ?')
        
        
        nb_coup = 0

        while nb_coup < nb_essais:

            reste = nb_essais - nb_coup

            print(f'\t- Il vous reste {reste} essai(s)')
            
            def demande_saisie():
                global nb_user

                try:
                    nb_user = int(input("Entrez un nombre ! (Vous avez 10 secondes max) : \n"))

                except ValueError:
                    print("Entrée invalide. Veuillez entrer un nombre.")
                    nb_user = None  
            
            debut_essai = time.time()
            nb_user = None
            
            thread_saisie = threading.Thread(target=demande_saisie)
            thread_saisie.start()


            while thread_saisie.is_alive():
                
                if time.time() - debut_essai > TEMPS_MAX:
                    nb_essais-=1
                    print(f"Vous avez dépassé le délai de {TEMPS_MAX} secondes ! Vous perdez l'essai courant et il vous reste {nb_essais} essai(s) !")
                    print('Entrez un nombre !\n')
                    thread_saisie.join()
                    break

                time.sleep(0.1)  # Petite pause pour éviter une boucle trop rapide
            
          
            if nb_user is None:
                continue

            nb_coup += 1

            if nb_user > nb_ordi:
                print('Votre nombre est trop grand')
                
            elif nb_user < nb_ordi:
                print('Votre nombre est trop petit')
                
            else:
                print(f"Bingo ! Vous avez gagné en {nb_coup} coup(s) !")
                level += 1
                dernier_level = level
                enregistrer_score(name, level, dernier_level)
                break
        else:
            print("Vous n'avez plus d'essais")
            level-=level
        print(f"Le nombre était : {nb_ordi}")
        



        if nb_essais > 20 : 
            doubleG = 5 #0-5 tu double
            NormalG = 10#5-10 mise normal et plus de 10 tu perds ta mise
        if nb_essais <=20 :
            doubleG = 1#0-1 tu double
            NormalG = 2#2 tu recup ta mise et plus de 2 tu perds


            