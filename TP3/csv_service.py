# csv_service.py — tout ce qui concerne le stockage des données

import csv
import os
import logging
from config import OUTPUT_FILE  # nom du fichier depuis la config

logger = logging.getLogger(__name__)


class CsvService:
    """Service d'écriture des données dans un fichier CSV."""

    # Attribut de classe — partagé par toutes les instances
    FIELDNAMES = ['sender', 'subject', 'date', 'body']

    def __init__(self, filename=OUTPUT_FILE):
        """Initialise le service avec le nom du fichier de sortie."""
        self.filename = filename  # stocke le nom du fichier comme attribut

    def save(self, emails_data):
        """Sauvegarde une liste d'emails dans le CSV."""

        # Vérifie si le fichier existe pour savoir si on doit écrire le header
        file_exists = os.path.exists(self.filename)

        # Mode 'a' = append — ajoute sans écraser
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)

            # Header uniquement si le fichier est nouveau
            if not file_exists:
                writer.writeheader()

            for email in emails_data:
                writer.writerow(email)

        logger.info(f"{len(emails_data)} email(s) sauvegardé(s) dans {self.filename}")