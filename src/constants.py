"""
Configuration pour l'architecture modulaire
"""

import os

# Chemins de base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
RESULTS_DIR = os.path.join(OUTPUT_DIR, 'results')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')

# Configuration OCR
OCR_LANGUAGES = ['fr', 'en']
OCR_GPU = False

# Paramètres de détection
MIN_PLATE_LENGTH = 6
MAX_PLATE_LENGTH = 12
MIN_CONFIDENCE = 0.3

# Formats de plaques
PLATE_FORMATS = {
    'FR': [
        r'^[A-Z]{2}-\d{3}-[A-Z]{2}$',  # AB-123-CD
        r'^[A-Z]{2}\d{3}[A-Z]{2}$',     # AB123CD
    ],
    'EU': [
        r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,2}$',
    ]
}