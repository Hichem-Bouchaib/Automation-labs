# main.py — point d'entrée et orchestrateur
# Ce fichier ne contient PAS de logique métier
# Il instancie les services et coordonne le workflow

import logging
from email_service import EmailService   # service Gmail
from csv_service import CsvService       # service stockage

# Configuration du logger global — format avec horodatage
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run():
    """Lance le workflow complet d'automatisation."""
    try:
        # Étape 1 : instancie le service Gmail — connexion OAuth au démarrage
        email_svc = EmailService()

        # Étape 2 : instancie le service de stockage
        csv_svc = CsvService()

        # Étape 3 : récupère les emails non lus
        messages = email_svc.get_unread_emails()

        if not messages:
            logger.info("Aucun email non lu. Arrêt du service.")
            return

        # Étape 4 : parse chaque email
        emails_data = []
        for msg in messages:
            email = email_svc.parse_email(msg['id'])
            emails_data.append(email)
            logger.info(f"Traité : {email['subject']} — de {email['sender']}")

        # Étape 5 : sauvegarde dans le CSV
        csv_svc.save(emails_data)
        logger.info("Workflow terminé avec succès.")

    except Exception as e:
        # Logue l'erreur avant que le programme s'arrête
        logger.error(f"Erreur dans le workflow : {e}")
        raise


# Lance le workflow uniquement si exécuté directement
if __name__ == '__main__':
    run()