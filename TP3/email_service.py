# email_service.py — tout ce qui concerne Gmail
# Principe : une classe = une responsabilité
# On reprend les fonctions du TP1 mais on les associe à la classe pour plus de clarté

import base64
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Importe la config centralisée — pas de valeurs en dur ici
from config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE, MAX_RESULTS

logger = logging.getLogger(__name__)  # logger propre à ce module


class EmailService:
    """Service de lecture des emails Gmail."""

    def __init__(self):
        """Initialise la connexion Gmail à la création de l'objet."""
        # self.service = attribut de l'instance, accessible dans toutes les méthodes
        self.service = self._authenticate()

    def _authenticate(self):
        """Gère l'authentification OAuth — méthode privée (préfixe _)."""
        creds = None

        # Charge le token existant si disponible
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # Si pas de token valide, lance le flow OAuth
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        logger.info("Connexion Gmail établie")
        return build('gmail', 'v1', credentials=creds)

    def get_unread_emails(self):
        """Récupère les emails non lus."""
        logger.info(f"Récupération des {MAX_RESULTS} derniers emails...")

        results = self.service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=MAX_RESULTS
        ).execute()

        messages = results.get('messages', [])
        logger.info(f"{len(messages)} email(s) trouvé(s)")
        return messages

    def parse_email(self, message_id):
        """Extrait les infos clés d'un email."""
        msg = self.service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()

        headers = msg['payload']['headers']
        sender  = next((h['value'] for h in headers if h['name'] == 'From'), 'Inconnu')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sans sujet')
        date    = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        body = ''
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif 'body' in msg['payload']:
            data = msg['payload']['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return {'sender': sender, 'subject': subject, 'date': date, 'body': body[:200]}