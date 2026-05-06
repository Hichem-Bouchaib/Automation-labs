# Modules Python standard
import os        # pour vérifier si un fichier existe
import base64    # pour décoder le contenu des emails
import csv       # pour écrire dans un fichier CSV
import logging   # pour tracer l'exécution (remplace print)

# Modules Google pour l'authentification OAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permission demandée à Google : lecture seule
# Principe du moindre privilège — jamais plus que nécessaire
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Configuration du logger : niveau INFO, format avec horodatage
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Crée un logger propre à ce fichier
logger = logging.getLogger(__name__)

def get_gmail_service():
    """Crée et retourne un service Gmail authentifié."""
    creds = None

    # Si un token existe déjà, on le charge pour éviter de se reconnecter
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(
            'token.json', SCOPES
        )

    # Si pas de token valide, on lance le processus d'authentification
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Token expiré mais renouvelable — on le rafraîchit
            creds.refresh(Request())
        else:
            # Pas de token — ouvre le navigateur pour demander l'autorisation
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Sauvegarde le token pour les prochaines exécutions
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Crée le service Gmail v1 avec les credentials validés
    service = build('gmail', 'v1', credentials=creds)
    logger.info("Connexion Gmail établie avec succès")
    return service


def get_unread_emails(service, max_results=10):
    """Récupère les emails non lus."""
    logger.info(f"Récupération des {max_results} derniers emails...")

    # Appel API : liste les messages dans INBOX non lus
    # Retourne uniquement des IDs — pas le contenu
    results = service.users().messages().list(
        userId='me',           # 'me' = l'utilisateur connecté
        labelIds=['INBOX', 'UNREAD'],  # filtre : boîte de réception non lus
        maxResults=max_results  # limite le nombre de résultats
    ).execute()

    # .get('messages', []) évite une erreur si aucun email trouvé
    messages = results.get('messages', [])
    logger.info(f"{len(messages)} email(s) trouvé(s)")
    return messages


def parse_email(service, message_id):
    """Extrait les infos clés d'un email."""

    # 2e requête API : récupère le contenu complet de l'email par son ID
    msg = service.users().messages().get(
        userId='me', id=message_id, format='full'
    ).execute()

    # Les headers contiennent les métadonnées : From, Subject, Date
    headers = msg['payload']['headers']

    # next() cherche le premier header qui correspond, sinon retourne la valeur par défaut
    sender  = next(
        (h['value'] for h in headers if h['name'] == 'From'), 'Inconnu'
    )
    subject = next(
        (h['value'] for h in headers if h['name'] == 'Subject'), 'Sans sujet'
    )
    date = next(
        (h['value'] for h in headers if h['name'] == 'Date'), ''
    )

    body = ''
    # Certains emails ont plusieurs parties (texte + HTML + pièces jointes)
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':  # on prend le texte brut
                data = part['body'].get('data', '')
                # Décode le contenu encodé en base64 par Gmail
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break  # on s'arrête dès qu'on a trouvé le texte
    elif 'body' in msg['payload']:
        # Email simple sans parties — le corps est directement dans payload
        data = msg['payload']['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')

    # Retourne un dictionnaire avec les 4 infos extraites
    # body[:200] = on tronque à 200 caractères pour ne pas surcharger le CSV
    return {
        'sender': sender, 'subject': subject,
        'date': date, 'body': body[:200]
    }


def save_to_csv(emails_data, filename='output.csv'):
    """Sauvegarde les emails dans un fichier CSV."""

    # Les 4 colonnes du fichier CSV
    fieldnames = ['sender', 'subject', 'date', 'body']

    # Vérifie si le fichier existe déjà pour savoir si on doit écrire le header
    file_exists = os.path.exists(filename)

    # Mode 'a' = append : ajoute sans écraser les données existantes
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # N'écrit le header (sender, subject...) que si le fichier est nouveau
        if not file_exists:
            writer.writeheader()

        # Écrit une ligne par email
        for email in emails_data:
            writer.writerow(email)

    logger.info(f"{len(emails_data)} email(s) sauvegardé(s) dans {filename}")



def main():
    try:
        # Étape 1 : connexion à Gmail
        service = get_gmail_service()

        # Étape 2 : récupérer les 5 derniers emails non lus
        messages = get_unread_emails(service, max_results=5)

        # Si aucun email non lu, on s'arrête proprement
        if not messages:
            logger.info("Aucun email non lu trouvé.")
            return

        # Étape 3 : parser le contenu de chaque email
        emails_data = []
        for msg in messages:
            email = parse_email(service, msg['id'])
            emails_data.append(email)
            logger.info(f"Traité : {email['subject']} — de {email['sender']}")

        # Étape 4 : sauvegarder tous les emails dans le CSV
        save_to_csv(emails_data)
        logger.info("Traitement terminé avec succès.")

    except Exception as e:
        # Logue l'erreur avant que le programme s'arrête
        # Sans ça, un crash en production serait silencieux
        logger.error(f"Erreur inattendue : {e}")
        raise  # relance l'erreur pour ne pas la masquer

# Ne lance main() que si on exécute ce fichier directement
if __name__ == '__main__':
    main()