import sqlite3
from database import Database
from game import Casino
from user import User

def main():
    try:
        conn = sqlite3.connect('scores.db')
        print("Connexion à la base de données réussie.")
        db = Database(conn)
        user = User(db)
        casino = Casino(user, db)
        casino.start_game()
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()