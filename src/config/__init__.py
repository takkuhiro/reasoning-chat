import os

from . import development, production


def get_settings():
    """
    Return the correct settings based on the environment
    """
    mode = os.getenv("MODE", "development")
    if mode == "production":
        return production.settings
    return development.settings
