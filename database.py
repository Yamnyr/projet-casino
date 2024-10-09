import sqlite3

class Database:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
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
        self.conn.commit()

    def enregistrer_score(self, name_user, level, dernier_level, solde):
        try:
            self.cursor.execute("SELECT * FROM utilisateurs WHERE pseudo = ?", (name_user,))
            result = self.cursor.fetchone()

            if result:
                ancien_level = result[1]
                if level > ancien_level:
                    self.cursor.execute("UPDATE utilisateurs SET level = ?, dernier_level = ?, argent = ? WHERE pseudo = ?",
                                    (level, dernier_level, solde, name_user))
                    print(f"\033[32mSuper ! Vous passez au Level {level}.\033[0m")
                else:
                    self.cursor.execute("UPDATE utilisateurs SET dernier_level = ?, argent = ? WHERE pseudo = ?",
                                   (dernier_level, solde, name_user))
            else:
                self.cursor.execute("INSERT INTO utilisateurs (pseudo, level, dernier_level, argent) VALUES (?, ?, ?, ?)",
                               (name_user, level, dernier_level, solde))
                print(f"\033[32mNiveau de {name_user} enregistré à {level}.\033[0m")

            self.conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du score : {e}")

    def mise_a_jour_statistiques(self, name_user, victoire, gain, perte, mise_max):
        try:
            self.cursor.execute("SELECT parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, gain_max, mise_max FROM utilisateurs WHERE pseudo = ?", (name_user,))
            stats = self.cursor.fetchone()

            if stats:
                parties_jouees = stats[0] + 1
                victoires = stats[1] + 1 if victoire else stats[1]
                defaites = stats[2] + 1 if not victoire else stats[2]
                argent_total_gagne = stats[3] + gain
                argent_total_perdu = stats[4] + perte
                gain_max = max(stats[5], gain)
                mise_max = max(stats[6], mise_max)

                self.cursor.execute('''
                    UPDATE utilisateurs
                    SET parties_jouees = ?, victoires = ?, defaites = ?, argent_total_gagne = ?, argent_total_perdu = ?, gain_max = ?, mise_max = ?
                    WHERE pseudo = ?
                ''', (parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, gain_max, mise_max, name_user))
            self.conn.commit()
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques : {e}")

    def get_user_info(self, name_user):
        self.cursor.execute("SELECT dernier_level, argent FROM utilisateurs WHERE pseudo = ?", (name_user,))
        return self.cursor.fetchone()

    def get_user_stats(self, name_user):
        self.cursor.execute("SELECT parties_jouees, victoires, defaites, argent_total_gagne, argent_total_perdu, level, gain_max, mise_max FROM utilisateurs WHERE pseudo = ?", (name_user,))
        return self.cursor.fetchone()