from sqlmodel import create_engine
from sqlalchemy import pool
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=pool.QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_recycle=3600,   # Recycle connexions après 1h
    connect_args={
        "sslmode": "require",  # Force SSL
        "connect_timeout": 10,
    }
)
