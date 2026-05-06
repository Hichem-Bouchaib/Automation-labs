# TP3 — Email Automation : Script → Service Python

Ce TP fait suite au TP1. On repart du même objectif — lire des emails Gmail et les enregistrer dans un CSV — mais on refactorise entièrement le code pour en faire un vrai service professionnel.

## Pourquoi ce TP ?

En TP1, on avait un script : un fichier unique avec des fonctions isolées et des valeurs en dur dans le code. Ça marche, mais c'est pas ce qu'on fait en entreprise.

Dans ce TP, on applique les principes d'un vrai service Python :
- **Séparation des responsabilités** — chaque fichier fait une seule chose
- **Configuration externalisée** — les paramètres sont dans un `.env`, jamais dans le code
- **Architecture en classes** — `EmailService` gère Gmail, `CsvService` gère le stockage
- **Logs par module** — chaque service trace ses propres actions

L'objectif : qu'un autre développeur puisse reprendre le code, le comprendre et le faire évoluer sans avoir à te demander quoi que ce soit.

## Ce qui change par rapport au TP1

| TP1 — Script | TP3 — Service |
|---|---|
| Tout dans `main.py` | Code réparti en 4 fichiers |
| Valeurs en dur dans le code | Config dans `.env` |
| Fonctions isolées | Classes avec responsabilités séparées |
| Logger global | Logger par module |
| Changer un paramètre = modifier le code | Changer un paramètre = modifier `.env` |

## Stack

- Python 3
- Google Gmail API
- google-auth, google-api-python-client
- python-dotenv

## Structure du projet

```
TP3/
├── .env              # variables de configuration — jamais sur GitHub
├── .gitignore
├── config.py         # charge et expose la configuration
├── email_service.py  # classe EmailService — tout ce qui concerne Gmail
├── csv_service.py    # classe CsvService — tout ce qui concerne le stockage
├── main.py           # orchestrateur — coordonne les services
└── requirements.txt  # dépendances
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Créer un projet sur [Google Cloud Console](https://console.cloud.google.com)
2. Activer l'API Gmail
3. Créer des identifiants OAuth 2.0 — Desktop App
4. Télécharger le JSON et le renommer `credentials.json`
5. Créer le fichier `.env` :

```
MAX_RESULTS=5
OUTPUT_FILE=output.csv
CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json
```

## Lancement

```bash
python main.py
```

La première fois, une fenêtre Google s'ouvre dans le navigateur. Une fois autorisé, `token.json` est sauvegardé pour les prochaines exécutions.

## Sécurité

`.env`, `credentials.json` et `token.json` sont exclus du repo via `.gitignore`.
