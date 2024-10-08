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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        pseudo TEXT PRIMARY KEY,
        level INTEGER,
        dernier_level INTEGER,
        argent INTEGER,
        parties_jouees INTEGER DEFAULT 0,
        victoires INTEGER DEFAULT 0,
        defaites INTEGER DEFAULT 0,
        argent_total_gagne INTEGER DEFAULT 0,
        argent_total_perdu INTEGER DEFAULT 0,
        gain_max INTEGER DEFAULT 0,
        mise_max INTEGER DEFAULT 0
    )
''')
conn.commit()

def enregistrer_score(name_user, level, dernier_level, solde):
    try:
        cursor.execute("SELECT * FROM utilisateurs WHERE pseudo = ?", (name_user,))
        result = cursor.fetchone()

        if result:
            ancien_level = result[1]
            if level > ancien_level:
                cursor.execute("UPDATE utilisateurs SET level = ?, dernier_level = ?, argent = ? WHERE pseudo = ?",
                                (level, dernier_level, solde, name_user))
                print(f"\033[32mSuper ! Vous passez au Level {level}.\033[0m")
            else:
                cursor.execute("UPDATE utilisateurs SET dernier_level = ?, argent = ? WHERE pseudo = ?",
                               (dernier_level, solde, name_user))
        else:
            cursor.execute("INSERT INTO utilisateurs (pseudo, level, dernier_level, argent) VALUES (?, ?, ?, ?)",
                           (name_user, level, dernier_level, solde))
            print(f"\033[32mNiveau de {name_user} enregistré à {level}.\033[0m")

        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du score : {e}")

def mise_a_jour_statistiques(name_user, victoire, gain, perte):
    try:
        # Récupération des statistiques actuelles
        cursor.execute("SELECT parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, gain_max, mise_max FROM utilisateurs WHERE pseudo = ?", (name_user,))
        stats = cursor.fetchone()

        if stats:
            parties_jouees = stats[0] + 1  # Incrémente le nombre de parties jouées
            victoires = stats[1] + 1 if victoire else stats[1]  # Incrémente les victoires si victoire
            defaites = stats[2] + 1 if not victoire else stats[2]  # Incrémente les défaites si défaite
            argent_total_gagne = stats[3] + gain  # Ajoute le gain au total
            argent_total_perdu = stats[4] + perte  # Ajoute la perte au total

            gain_max = max(stats[5], gain)  # Nouveau gain max
            mise_max = max(stats[6], miseG)  # Nouvelle mise max

            cursor.execute('''
                UPDATE utilisateurs
                SET parties_jouees = ?, victoires = ?, defaites = ?, argent_total_gagne = ?, argent_total_perdu = ?, gain_max = ?, mise_max = ?
                WHERE pseudo = ?
            ''', (parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, gain_max, mise_max, name_user))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la mise à jour des statistiques : {e}")


def afficher_regles():
    reponse = input("\033[36mSouhaitez-vous afficher les règles du jeu (O/N) ?\033[0m \n").strip().lower()
    if reponse == 'o':
        print("""
        \033[34m* RÈGLES DU JEU *\033[0m
        - Le but est de deviner le nombre choisi par l'ordinateur.
        - Vous avez 3 niveaux :
          * Level 1 : Nombre entre 1 et 10, 3 essais
          * Level 2 : Nombre entre 1 et 20, 5 essais
          * Level 3 : Nombre entre 1 et 30, 7 essais
        - Chaque essai est limité à 10 secondes.
        - Si vous gagnez, vous pouvez quitter le jeu avec vos gains ou passer au level supérieur.
        """)

def demande_saisie():
    global nb_user
    try:
        nb_user = int(input("Entrez un nombre (en 10 secondes max) : \n"))
    except ValueError:
        print("\033[31mEntrée invalide. Veuillez entrer un nombre.\033[0m")
        nb_user = None  

def afficher_statistiques(name_user):
    try:
        cursor.execute("SELECT parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, level, gain_max, mise_max FROM utilisateurs WHERE pseudo = ?", (name_user,))
        stats = cursor.fetchone()

        if stats:
            parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, level, gain_max, mise_max  = stats
            print(f"\033[36m--------------------------------------------------------------------------------\033[0m")
            print(f"\033[34mVos meilleures statistiques :")
            print(f"\033[34m- Level le plus élevé atteint : {level}\033[0m")
            print(f"\033[34m- Argent total gagné : {argent_total_gagne} €\033[0m")
            print(f"\033[34m- Argent total perdu : {argent_total_perdu} €\033[0m")
            print(f"\033[34m- Parties jouées : {parties_jouees}\033[0m")
            print(f"\033[34m- Victoires : {victoires}\033[0m")                        
            print(f"\033[34m- Défaites : {defaites}\033[0m")
            print(f"\033[34m- Plus grosse mise : {mise_max} €\033[0m")
            print(f"\033[34m- Plus gros gain : {gain_max} €\033[0m")
        else:
            print(f"\033[31mAucune statistique trouvée pour {name_user}.\033[0m")
    except Exception as e:
        print(f"Erreur lors de l'affichage des statistiques : {e}")


miseG= 0
TEMPS_MAX = 10       
level = 1
afficher_regles()

name_user = input('\033[36mQuel est votre pseudo ?\033[0m \n')

# Récupération du dernier niveau joué et de l'argent si l'utilisateur existe
cursor.execute("SELECT dernier_level, argent FROM utilisateurs WHERE pseudo = ?", (name_user,))
result = cursor.fetchone()

if result:
    dernier_level = result[0]
    solde = result[1]
    level = dernier_level  
    print(f"\033[36mRebonjour {name_user}, Content de vous revoir au Casino, prêt pour un nouveau challenge !\033[0m")
    if solde == 0:  
        dernier_level = 1
        solde = int(input("\033[36m Vous avez perdu tous votre solde durant les partie précédentes Quel montant voulez-vous redéposer ?\033[0m \n"))
        enregistrer_score(name_user, level, dernier_level, solde)
else:
    dernier_level = 1
    solde = 0
    enregistrer_score(name_user, level, dernier_level, solde)
    while True:
        solde = input("\033[36mQuel montant voulez-vous déposer ?\033[0m \n")
        try:
            solde = int(solde)
            if solde > 0:
                solde = solde
                break
        except:
            print("\033[31mEntrée invalide. Veuillez entrer un nombre.\033[0m")
    nb_user = None  

while True:
    if level > 3:
        level = int(input(f'{name_user}, quel niveau voulez-vous ? : '))
    if level < 1:
        level = 1
    nb_essais = 3 + (2 * level - 2)

    print('--------------------------------------------------------------------------------')
    print(f'\033[35mVous êtes au niveau : {level}\033[0m')

    nb_python = randrange(1, level * 10 + 1)
    while True:
        try:
            mise = int(input(f"\033[36mEntrez votre mise : \nVous avez {solde} € sur votre compte :\033[0m \n"))
            
            if mise > solde:
                print(f"\033[31mErreur, votre mise est plus élevée que votre solde. Entrer une mise inférieure ou égale à {solde} € :\033[0m")
            elif mise <= 0:
                print("\033[31mLe montant saisi n'est pas valide. Entrer SVP un montant entre 1 et 10 € :\033[0m")
            else:
                print(f"\033[36mVous avez misé {mise}.\033[0m")
                if mise > miseG :
                    miseG = mise                                                                                                                             #modif ici
                break
        except ValueError:
            print("\033[31mLe montant saisi n'est pas valide. Entrer SVP un montant entre 1 et 10 € :\033[0m")

    print(f'\t- \033[36mAlors mon nombre est entre 1 et {level * 10}. Devinez lequel ?\033[0m')
    print(f'\t- \033[36mVous avez {nb_essais} essais.\033[0m')

    nb_coup = 0

    while nb_coup < nb_essais:

        reste = nb_essais - nb_coup

        if reste == 1:
            print(f"\033[33mIl vous reste une chance !\033[0m")
        else:
            print(f'\t- \033[36mIl vous reste {reste} essai(s)\033[0m')
        
        debut_essai = time.time()
        nb_user = None
        
        thread_saisie = threading.Thread(target=demande_saisie)
        thread_saisie.start()

        while thread_saisie.is_alive():
            if time.time() - debut_essai > TEMPS_MAX:
                nb_essais -= 1
                print(f"\033[31mVous avez dépassé le délai de {TEMPS_MAX} secondes ! Vous perdez l'essai courant et il vous reste {nb_essais} essai(s) !\033[0m")
                thread_saisie.join()
                break

            time.sleep(0.1) 
        
        if nb_user is None:
            continue

        nb_coup += 1

        if nb_user > nb_python:
            print(f'\033[33mVotre nombre est trop grand !\033[0m')
        elif nb_user < nb_python:
            print(f'\033[33mVotre nombre est trop petit !\033[0m')
        else:
            gain = mise * 2 if nb_coup == 1 else mise
            solde += gain - mise
            print(f"\033[32mBingo {name_user}, vous avez gagné en {nb_coup} coup(s) et vous avez emporté {gain} € !\033[0m")                                                                                                                                    #modif ici
            level += 1
            dernier_level = level
            enregistrer_score(name_user, level, dernier_level, solde)
            mise_a_jour_statistiques(name_user, victoire=True, gain=gain, perte=0)  # Victoire, gain ajouté

            break
    else:
        print(f"\033[31mVous avez perdu ! Mon nombre était {nb_python} !\033[0m")
        solde -= mise
        enregistrer_score(name_user, level, dernier_level, solde)
        mise_a_jour_statistiques(name_user, victoire=False, gain=0, perte=mise)  # Défaite, perte enregistrée

    afficher_stats = input("\033[36mSouhaitez-vous consulter vos statistiques (O/N) ?\033[0m \n").strip().lower()
    if afficher_stats == 'o':
        afficher_statistiques(name_user)
    continuer = input("\033[36mSouhaitez-vous continuer la partie (O/N) ?\033[0m \n").strip().lower()
    if continuer != 'o':
        print(f"\033[32mAu revoir ! Vous finissez la partie avec {solde} €.\033[0m")
        break
    else:
        if level == 2:
            print(f"\033[36mSuper ! Vous passez au Level 2.\nRappelez-vous, le principe est le même sauf que mon nombre est maintenant entre 1 et 20 et vous avez le droit à 5 essais !\033[0m")
        elif level == 3:
            print(f"\033[36mSuper ! Vous passez au Level 3.\nRappelez-vous, le principe est le même sauf que mon nombre est entre 1 et 30 et vous avez le droit à 7 essais !\033[0m")

        elif level == 4:
            print(f"\033[32mFélicitations {name_user}, vous avez atteint le niveau maximum !\033[0m")
            continuer = input("\033[36mSouhaitez-vous recommencer depuis le Level 1 (O/N) ?\033[0m \n").strip().lower()
            if continuer == 'o':
                level = 1
                dernier_level = 1
                enregistrer_score(name_user, level, dernier_level, solde)
                print(f"\033[36mRepartons pour un nouveau challenge depuis le Level 1 !\033[0m")
            else:
                print(f"\033[32mAu revoir {name_user} ! Vous finissez la partie avec {solde} €.\033[0m")
                
                break
       
    print("\033[36mMerci d'avoir joué ! À la prochaine fois !\033[0m")


