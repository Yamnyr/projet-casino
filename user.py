class User:
    def __init__(self, db):
        self.db = db
        self.name = ""
        self.level = 1
        self.dernier_level = 1
        self.solde = 0

    def initialize(self):
        self.name = input('\033[36mQuel est votre pseudo ?\033[0m \n')
        result = self.db.get_user_info(self.name)

        if result:
            self.dernier_level, self.solde = result
            self.level = self.dernier_level
            print(f"\033[36mRebonjour {self.name}, Content de vous revoir au Casino, prêt pour un nouveau challenge !\033[0m")
            if self.solde == 0:
                self.dernier_level = 1
                self.solde = int(input("\033[36m Vous avez perdu tout votre solde durant les parties précédentes. Quel montant voulez-vous redéposer ?\033[0m \n"))
                self.db.enregistrer_score(self.name, self.level, self.dernier_level, self.solde)
        else:
            while True:
                solde = input("\033[36mQuel montant voulez-vous déposer ?\033[0m \n")
                try:
                    solde = int(solde)
                    if solde > 0:
                        self.solde = solde
                        break
                except:
                    print("\033[31mEntrée invalide. Veuillez entrer un nombre.\033[0m")
            self.db.enregistrer_score(self.name, self.level, self.dernier_level, self.solde)

    def update_score(self, level, dernier_level, solde):
        self.level = level
        self.dernier_level = dernier_level
        self.solde = solde
        self.db.enregistrer_score(self.name, level, dernier_level, solde)

    def update_stats(self, victoire, gain, perte, mise_max):
        self.db.mise_a_jour_statistiques(self.name, victoire, gain, perte, mise_max)

    def display_stats(self):
        stats = self.db.get_user_stats(self.name)
        if stats:
            parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, level, gain_max, mise_max = stats
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
            print(f"\033[31mAucune statistique trouvée pour {self.name}.\033[0m")