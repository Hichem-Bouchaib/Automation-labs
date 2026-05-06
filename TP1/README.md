# TP1 — Email Automation via Gmail API

Script Python qui se connecte à une boîte Gmail via l'API Google, récupère les emails non lus et les enregistre automatiquement dans un fichier CSV.

## Ce que ça fait

1. S'authentifie à Gmail via OAuth 2.0 (aucun mot de passe dans le code)
2. Récupère les 5 derniers emails non lus de la boîte de réception
3. Extrait l'expéditeur, le sujet, la date et le corps de chaque email
4. Sauvegarde les données dans `output.csv` sans écraser les entrées précédentes

## Stack

- Python 3
- Google Gmail API
- google-auth, google-api-python-client

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
5. Le placer à la racine du projet

## Lancement

```bash
python main.py
```

La première fois, une fenêtre Google s'ouvre dans le navigateur. Une fois autorisé, `token.json` est sauvegardé pour les prochaines exécutions.

## Sécurité

`credentials.json` et `token.json` sont exclus du repo via `.gitignore`. Ne jamais les commiter.