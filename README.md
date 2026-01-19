# Mini-Projet ALPR - Reconnaissance de Plaques d'Immatriculation

## Description
Système simple de reconnaissance automatique de plaques d'immatriculation.

## Structure du projet
mini_alpr/
├── data/
│   ├── input/           # Images d'entrée
│   └── output/          # Résultats
│       ├── results/     # Images avec détections
│       └── reports/     # Rapports texte et CSV
├── src/                 # Architecture modulaire
│   ├── constants.py     # Configuration et chemins
│   ├── detector.py      # Détection plaques
│   ├── ocr_engine.py    # Moteur OCR (EasyOCR)
│   ├── preprocessor.py  # Traitement images
│   ├── utils.py         # Fonctions utilitaires
│   └── io_manager.py    # Gestion input/output
├── alpr_modular.py      # Programme principal
├── requirements.txt     # Dépendances
├── alpr_io.py             # (tout-en-un)
└── README.md             # Documentation

## Installation
### 1. Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances
# Créer venv (si pas fait)
py -3.10 -m venv venv310
venv310\Scripts\activate.bat
pip install -r requirements.txt

##  Structure des dossiers :
# Créer la structure
mkdir -p data/input data/output/results data/output/reports
mkdir -p src

# Placer vos images dans data/input/

## Utilisation
# Traiter une image spécifique
python alpr_modular.py -i "chemin/image.jpg"

# Utiliser data/input/
python alpr_modular.py --data-input

# Traiter un dossier (batch)
python alpr_modular.py -d "chemin/dossier"

# Mode interactif
python alpr_modular.py
