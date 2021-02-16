import os


class Config:
    DEBUG = bool(os.getenv("DEBUG"))
