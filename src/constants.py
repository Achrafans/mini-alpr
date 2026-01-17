"""
Constantes et configurations du projet
"""

# Paramètres EasyOCR
OCR_LANGUAGES = ['en', 'fr']  # Anglais et Français
OCR_GPU = False  # Mettre à True si vous avez un GPU

# Paramètres de détection
MIN_PLATE_LENGTH = 6
MAX_PLATE_LENGTH = 12
MIN_CONFIDENCE = 0.3

# Formattage
PLATE_FORMATS = {
    'FR': [
        r'^[A-Z]{2}-\d{3}-[A-Z]{2}$',  # AB-123-CD
        r'^[A-Z]{2}\d{3}[A-Z]{2}$',     # AB123CD
    ],
    'EU': [
        r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,2}$',
    ]
}

# Chemins
DEFAULT_INPUT_DIR = 'data/input/'
DEFAULT_OUTPUT_DIR = 'data/output/'