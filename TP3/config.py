# config.py — charge les variables d'environnement
# Ce fichier est le seul endroit où on lit la config

import os
from dotenv import load_dotenv  # charge le fichier .env

# Lit le fichier .env et injecte les variables
load_dotenv()

# Expose les valeurs de config sous forme de constantes
# os.getenv(clé, valeur_par_défaut) — la valeur par défaut est un filet de sécurité
MAX_RESULTS = int(os.getenv('MAX_RESULTS', 10))
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'output.csv')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.json')

# Scopes Gmail — lecture seule, principe du moindre privilège
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']