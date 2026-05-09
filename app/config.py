### FastAPI application configuration file

from fastapi import FastAPI
import os
from pathlib import Path
from dotenv import load_dotenv

# Read the .env file and load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# db URL
DATABASE_URL = os.getenv("DATABASE_URL")
# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
