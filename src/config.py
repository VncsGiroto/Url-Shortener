from multiprocessing import pool
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_MIN_CONN = int(os.getenv("DB_MIN_CONN", 1))
    DB_MAX_CONN = int(os.getenv("DB_MAX_CONN", 10))