# — init minimal de la base
# Ce script sert juste à créer les tables si tu souhaites le lancer à la main (python -m backend.scripts.init_db par exemple).

# Chemin d'accès: 
# backend/scripts/init_db.py

"""
Script très simple pour initialiser la base SQLite.

Tu peux l'exécuter avec :
    python -m backend.scripts.init_db
(en étant dans le dossier racine du projet).
"""

from backend.app.db import engine, Base
from backend.app import models  # pour que les modèles soient enregistrés


def init_db():
    print("Création des tables dans la base SQLite...")
    Base.metadata.create_all(bind=engine)
    print("Terminé.")


if __name__ == "__main__":
    init_db()
