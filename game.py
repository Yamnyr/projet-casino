from random import randrange
import time
import threading


class Casino:
    def __init__(self, user, db):
        self.user = user
        self.db = db
        self.TEMPS_MAX = 10
        self.mise_max = 0

    def afficher_regles(self):
        while True:
            reponse = input("\033[36mSouhaitez-vous afficher les règles du jeu (O/N) ?\033[0m \n").strip().lower()
            if reponse in ['o', 'n']:
                break
            print("\033[31mRéponse invalide. Veuillez entrer 'O' pour Oui ou 'N' pour Non.\033[0m")

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

    def demande_saisie(self):
        try:
            self.nb_user = int(input("Entrez un nombre (en 10 secondes max) : \n"))
            if self.nb_user < 1 or self.nb_user > self.user.level * 10:
                raise ValueError
        except ValueError:
            print(f"\033[31mEntrée invalide. Veuillez entrer un nombre entre 1 et {self.user.level * 10}.\033[0m")
            self.nb_user = None

    def demande_mise(self):
        while True:
            try:
                mise = int(
                    input(f"\033[36mEntrez votre mise : \nVous avez {self.user.solde} € sur votre compte :\033[0m \n"))

                if mise > self.user.solde:
                    print(
                        f"\033[31mErreur, votre mise est plus élevée que votre solde. Entrer une mise inférieure ou égale à {self.user.solde} € :\033[0m")
                elif mise <= 0:
                    print("\033[31mLe montant saisi n'est pas valide. Entrer SVP un montant positif :\033[0m")
                else:
                    return mise
            except ValueError:
                print("\033[31mLe montant saisi n'est pas valide. Veuillez entrer un nombre entier positif.\033[0m")

    def jouer_tour(self):
        nb_python = randrange(1, self.user.level * 10 + 1)
        nb_essais = 3 + (2 * self.user.level - 2)

        mise = self.demande_mise()
        print(f"\033[36mVous avez misé {mise}.\033[0m")
        if mise > self.mise_max:
            self.mise_max = mise

        print(f'\t- \033[36mAlors mon nombre est entre 1 et {self.user.level * 10}. Devinez lequel ?\033[0m')
        print(f'\t- \033[36mVous avez {nb_essais} essais.\033[0m')

        for nb_coup in range(nb_essais):
            reste = nb_essais - nb_coup
            if reste == 1:
                print(f"\033[33mIl vous reste une chance !\033[0m")
            else:
                print(f'\t- \033[36mIl vous reste {reste} essai(s)\033[0m')

            debut_essai = time.time()
            self.nb_user = None

            thread_saisie = threading.Thread(target=self.demande_saisie)
            thread_saisie.start()

            while thread_saisie.is_alive():
                if time.time() - debut_essai > self.TEMPS_MAX:
                    print(
                        f"\033[31mVous avez dépassé le délai de {self.TEMPS_MAX} secondes ! Vous perdez cet essai !\033[0m")
                    thread_saisie.join()
                    break

                time.sleep(0.1)

            if self.nb_user is None:
                continue

            if self.nb_user > nb_python:
                print(f'\033[33mVotre nombre est trop grand !\033[0m')
            elif self.nb_user < nb_python:
                print(f'\033[33mVotre nombre est trop petit !\033[0m')
            else:
                gain = mise * 2 if nb_coup == 0 else mise
                self.user.solde += gain - mise
                print(
                    f"\033[32mBingo {self.user.name}, vous avez gagné en {nb_coup + 1} coup(s) et vous avez emporté {gain} € !\033[0m")
                self.user.level += 1
                self.user.dernier_level = self.user.level
                self.user.update_score(self.user.level, self.user.dernier_level, self.user.solde)
                self.user.update_stats(victoire=True, gain=gain, perte=0, mise_max=self.mise_max)
                return True

        print(f"\033[31mVous avez perdu ! Mon nombre était {nb_python} !\033[0m")
        self.user.solde -= mise
        self.user.update_score(self.user.level, self.user.dernier_level, self.user.solde)
        self.user.update_stats(victoire=False, gain=0, perte=mise, mise_max=self.mise_max)
        return False

    def demande_oui_non(self, question):
        while True:
            reponse = input(question).strip().lower()
            if reponse in ['o', 'n']:
                return reponse == 'o'
            print("\033[31mRéponse invalide. Veuillez entrer 'O' pour Oui ou 'N' pour Non.\033[0m")

    def start_game(self):
        self.afficher_regles()
        self.user.initialize()

        while True:
            print('--------------------------------------------------------------------------------')
            print(f'\033[35mVous êtes au niveau : {self.user.level}\033[0m')

            self.jouer_tour()

            if self.demande_oui_non("\033[36mSouhaitez-vous consulter vos statistiques (O/N) ?\033[0m \n"):
                self.user.display_stats()

            if not self.demande_oui_non("\033[36mSouhaitez-vous continuer la partie (O/N) ?\033[0m \n"):
                print(f"\033[32mAu revoir ! Vous finissez la partie avec {self.user.solde} €.\033[0m")
                break
            else:
                if self.user.level == 2:
                    print(
                        f"\033[36mSuper ! Vous passez au Level 2.\nRappelez-vous, le principe est le même sauf que mon nombre est maintenant entre 1 et 20 et vous avez le droit à 5 essais !\033[0m")
                elif self.user.level == 3:
                    print(
                        f"\033[36mSuper ! Vous passez au Level 3.\nRappelez-vous, le principe est le même sauf que mon nombre est entre 1 et 30 et vous avez le droit à 7 essais !\033[0m")
                elif self.user.level == 4:
                    print(f"\033[32mFélicitations {self.user.name}, vous avez atteint le niveau maximum !\033[0m")
                    if self.demande_oui_non("\033[36mSouhaitez-vous recommencer depuis le Level 1 (O/N) ?\033[0m \n"):
                        self.user.level = 1
                        self.user.dernier_level = 1
                        self.user.update_score(self.user.level, self.user.dernier_level, self.user.solde)
                        print(f"\033[36mRepartons pour un nouveau challenge depuis le Level 1 !\033[0m")
                    else:
                        print(
                            f"\033[32mAu revoir {self.user.name} ! Vous finissez la partie avec {self.user.solde} €.\033[0m")
                        break

        print("\033[36mMerci d'avoir joué ! À la prochaine fois !\033[0m")