import sqlite3
from random import randrange
import time
import threading

# Connexion à la base de données SQLite
try:
    conn = sqlite3.connect('scores.db')
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

def enregistrer_score(name, level, dernier_level, argent):
    try:
        cursor.execute("SELECT * FROM utilisateurs WHERE pseudo = ?", (name,))
        result = cursor.fetchone()

        if result:
            ancien_level = result[1]
            # Mettre à jour les deux champs si le nouveau niveau est meilleur
            if level > ancien_level:
                cursor.execute("UPDATE utilisateurs SET level = ?, dernier_level = ?, argent = ? WHERE pseudo = ?",
                                (level, dernier_level, argent, name))
                print(f"\033[32mFélicitations {name}, votre niveau a été mis à jour à {level} !\033[0m")
            else:
                cursor.execute("UPDATE utilisateurs SET dernier_level = ?, argent = ? WHERE pseudo = ?",
                               (dernier_level, argent, name))
                print(f"\033[33m{name}, votre niveau actuel est inférieur à votre meilleur niveau ({ancien_level}).\033[0m")
        else:
            # Insertion d'un nouvel utilisateur avec le niveau actuel et dernier niveau
            cursor.execute("INSERT INTO utilisateurs (pseudo, level, dernier_level, argent) VALUES (?, ?, ?, ?)",
                           (name, level, dernier_level, argent))
            print(f"\033[32mNiveau de {name} enregistré à {level}.\033[0m")

        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du score : {e}")
        

def demande_saisie():
    global nb_user
    try:
        nb_user = int(input("Entrez un nombre (en 10 secondes max) : \n"))
    except ValueError:
        print("Entrée invalide. Veuillez entrer un nombre.")
        nb_user = None  

TEMPS_MAX = 10       
level = 1
name = input('\033[36mJe suis Python. Quel est votre pseudo ?\033[0m \n')
# Récupération du dernier niveau joué (dernier_level) si l'utilisateur existe
cursor.execute("SELECT dernier_level, argent FROM utilisateurs WHERE pseudo = ?", (name,))
result = cursor.fetchone()

if result:
    dernier_level = result[0]
    argent = result[1]
    level = dernier_level  # On fixe le niveau actuel au dernier joué
    print(f"\033[36mRe-bienvenue {name} ! Vous recommencez à votre dernier niveau : {level}.\033[0m")
else:
    dernier_level = 1
    argent = int(input("\033[36mQuel montant voulez-vous déposer ?\033[0m \n"))
    enregistrer_score(name, level, dernier_level, argent)

while True:
    if level > 3:
        level = int(input(f'{name}, quel niveau voulez-vous ? : '))
    if level < 1:
        level = 1
    nb_essais = 3 + (2 * level - 2)

    print('--------------------------------------------------------------------------------')
    print(f'\033[35mVous êtes au niveau : {level}\033[0m')

    nb_ordi = randrange(1, level * 10 + 1)
    while True:
        try:
            mise = int(input(f"\033[36mQuel montant voulez-vous miser ? \nVous avez {argent} € sur votre compte :\033[0m \n"))
            
            if mise > argent:
                print(f"\033[31mVous ne pouvez pas miser plus que {argent}. Veuillez réessayer.\033[0m")
            elif mise <= 0:
                print("\033[31mLa mise doit être un montant positif. Veuillez réessayer.\033[0m")
            else:
                print(f"\033[36mVous avez misé {mise}.\033[0m")
                break
        except ValueError:
            print("\033[31mEntrée invalide. Veuillez entrer un nombre entier.\033[0m")

    print(f'\t- \033[36mJe viens de penser à un nombre entre 1 et {level * 10}. Devinez lequel ?\033[0m')
    print(f'\t- \033[36mVous avez {nb_essais} essais.\033[0m')

    nb_coup = 0

    while nb_coup < nb_essais:

        reste = nb_essais - nb_coup

        print(f'\t- \033[36mIl vous reste {reste} essai(s)\033[0m')
        
        debut_essai = time.time()
        nb_user = None
        
        thread_saisie = threading.Thread(target=demande_saisie)
        thread_saisie.start()

        while thread_saisie.is_alive():
            if time.time() - debut_essai > TEMPS_MAX:
                nb_essais -= 1
                print(f"\033[31mVous avez dépassé le délai de {TEMPS_MAX} secondes ! Vous perdez l'essai courant, il vous reste {nb_essais} essai(s) !\033[0m")
                thread_saisie.join()
                break

            time.sleep(0.1)  # Petite pause pour éviter une boucle trop rapide
        
        if nb_user is None:
            continue

        nb_coup += 1

        if nb_user > nb_ordi:
            print(f'\033[33mVotre nombre est trop grand.\033[0m')
        elif nb_user < nb_ordi:
            print(f'\033[33mVotre nombre est trop petit.\033[0m')
        else:
            print(f"\033[32mBingo {name}, vous avez gagné en {nb_coup} coup(s) !\033[0m")
            
            if nb_coup == 1:
                gains = mise * 2
                print(f"\033[32mFélicitations ! Vous gagnez le double de votre mise : {gains} €.\033[0m")
            elif nb_coup <= 2 * level:
                gains = mise
                print(f"\033[32mBravo ! Vous gagnez exactement votre mise : {gains} €.\033[0m")
            else:
                gains = 0
                print(f"\033[33mVous avez deviné, mais pas dans le nombre optimal de coups. Vous ne gagnez rien cette fois.\033[0m")
            
            argent += (gains - mise)
            level += 1
            dernier_level = level
            enregistrer_score(name, level, dernier_level, argent)
            break
    else:
        print(f"\033[31mVous avez perdu ! Mon nombre était {nb_ordi} !\033[0m")
        argent -= mise
        enregistrer_score(name, level, dernier_level, argent)

    continuer = input("\033[36mSouhaitez-vous continuer la partie (O/N) ?\033[0m \n").strip().lower()
    if continuer != 'o':
        print(f"\033[32mAu revoir {name}! Vous finissez la partie avec {argent} €.\033[0m")
        break
