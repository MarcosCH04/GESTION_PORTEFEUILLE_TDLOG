# # On passe sur SQLite.
# # Dans ce code, le backend n’utilise pas encore fortement SQLAlchemy, mais ça prépare le terrain.

# # Chemin d'accès:
# # backend/app/db.py

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os

# # URL de la base SQLite.
# # Par simplicité : fichier app.db dans le dossier backend
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DB_PATH = os.path.join(BASE_DIR, "app.db")
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# # create_engine pour SQLite (check_same_thread=False pour FastAPI)
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     """
#     Dépendance FastAPI : fournit une session de base de données,
#     et la ferme automatiquement après usage.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
