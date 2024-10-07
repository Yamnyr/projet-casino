import sqlite3
from random import randrange
import time
import threading

# Connexion à la base de données SQLite
conn = sqlite3.connect('levels.db')
cursor = conn.cursor()

# Création de la table si elle n'existe pas déjà
cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        pseudo TEXT PRIMARY KEY,
        level INTEGER
    )
''')
conn.commit()

def enregistrer_score(name, level):
    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT * FROM utilisateurs WHERE pseudo = ?", (name,))
    result = cursor.fetchone()
    
    if result:
        # Si l'utilisateur existe déjà, mettre à jour le niveau s'il est meilleur
        ancien_level = result[1]
        if level > ancien_level:
            cursor.execute("UPDATE utilisateurs SET level = ? WHERE pseudo = ?", (level, name))
            print(f"Félicitations {name}, votre niveau a été mis à jour à {level} !")
        else:
            print(f"{name}, votre niveau actuel est inférieur à votre meilleur niveau ({ancien_level}).")
    else:
        # Sinon, insérer un nouveau record
        cursor.execute("INSERT INTO utilisateurs (pseudo, level) VALUES (?, ?)", (name, level))
        print(f"Niveau de {name} enregistré à {level}.")
    
    conn.commit()

def attendre_reponse(stop_event):
    try:
        nb_user = int(input("Entrez un nombre (en 10 secondes max) : "))
        # Si l'utilisateur répond avant 10 secondes, on signale au timer de s'arrêter
        stop_event.set()
        print(f"Vous avez répondu : {nb_user}")
        return nb_user
    except ValueError:
        print("Entrée invalide. Veuillez entrer un nombre.")
        return None

def time_out(stop_event):
    # Attente jusqu'à ce que l'événement soit défini, ou expiration du délai de 10 secondes
    if not stop_event.wait(10):  
        print("Temps écoulé ! Vous n'avez pas répondu à temps.\n")

def main_game():
    level = 1

    name = input('Je suis Python. Quel est votre pseudo ? \n')
    while True:
        # Limite le niveau entre 1 et 3
        if level > 3:
            level = int(input(f'{name}, quel est votre niveau ? (1 à 3) : '))
        if level < 1:
            level = 1
        
        nb_essais = 3 + (2 * level - 2)
        print(f'\nVous avez choisi le niveau : {level}')
        
        nb_ordi = randrange(1, level * 10 + 1)
        print('______________________________________________________________________________')
        print(f'\t- Je viens de penser à un nombre entre 1 et {level * 10}. Devinez lequel ?')

        nb_coup = 0

        while nb_coup < nb_essais:
            reste = nb_essais - nb_coup
            print(f'\t- Il vous reste {reste} essai(s)')

            # Créez un événement pour indiquer quand le timer doit être arrêté
            stop_event = threading.Event()

            # Lancer le thread du timer
            timer_thread = threading.Thread(target=time_out, args=(stop_event,))
            timer_thread.start()

            # Attendre la réponse de l'utilisateur
            nb_user = attendre_reponse(stop_event)

            # Attendre que le thread du timer se termine, au cas où il reste actif
            timer_thread.join()

            if nb_user is None:
                continue

            nb_coup += 1

            if nb_user > nb_ordi:
                print('Votre nombre est trop grand')
            elif nb_user < nb_ordi:
                print('Votre nombre est trop petit')
            else:
                print(f"Bingo ! Vous avez gagné en {nb_coup} coup(s) !\n")
                level += 1  # Passe au niveau suivant
                enregistrer_score(name, level)  # Enregistre le nouveau niveau
                break
        else:
            print("Vous n'avez plus d'essais")
        
        print(f"Le nombre était : {nb_ordi}")

if __name__ == "__main__":
    try:
        main_game()
    finally:
        conn.close()  # Fermer la connexion à la base de données lorsqu'on quitte le jeu
