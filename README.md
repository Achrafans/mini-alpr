# Mini-Projet ALPR - Reconnaissance de Plaques d'Immatriculation

## Description
Système simple de reconnaissance automatique de plaques d'immatriculation.

## Installation
### 1. Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

## Structure du projet
mini_alpr/
├── run.py              # Script principal
├── requirements.txt    # Dépendances
├── README.md          # Ce fichier
├── src/               # Code source
│   ├── main.py        # Programme principal
│   ├── ocr_engine.py  # Moteur OCR
│   ├── detector.py    # Détecteur
│   ├── preprocessor.py # Pré-traitement
│   ├── utils.py       # Utilitaires
│   └── constants.py   # Configurations
├── data/              # Données
│   ├── input/         # Images à tester
│   └── output/        # Résultats
└── tests/             # Tests unitaires

## Utilisation

## Mode simple (une image)
python run.py --image data/input/test_plate.jpg

## Mode debug (plus d'informations)
python run.py --image data/input/test_plate.jpg --debug

## Mode batch (tout un dossier)
python run.py --image data/input/ --batch --output results/

## Avec dossier de sortie personnalisé
python run.py --image test.jpg --output mon_dossier/



