"""
Moteur OCR pour la lecture des plaques
"""

import easyocr
import re
from .constants import OCR_LANGUAGES, OCR_GPU, PLATE_FORMATS

class OCREngine:
    """Moteur OCR basé sur EasyOCR"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.reader = easyocr.Reader(
            OCR_LANGUAGES,
            gpu=OCR_GPU,
            model_storage_directory='data/models/',
            download_enabled=True
        )
        
    def extract_text(self, image):
        """Extrait tout le texte d'une image"""
        try:
            # EasyOCR retourne: [(bbox, text, confidence), ...]
            results = self.reader.readtext(
                image,
                paragraph=False,
                detail=1
            )
            
            if self.debug:
                print(f"  Textes détectés: {len(results)}")
                for bbox, text, conf in results:
                    print(f"    '{text}' ({conf:.1%})")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur OCR: {e}")
            return []
    
    def clean_plate_text(self, text):
        """Nettoie et formate le texte d'une plaque"""
        # Supprimer espaces et caractères spéciaux
        cleaned = re.sub(r'[^\w\-]', '', text)
        
        # Convertir en majuscules
        cleaned = cleaned.upper()
        
        # Corriger les confusions courantes
        replacements = {
            '0': 'O',
            '1': 'I',
            '5': 'S',
            '8': 'B'
        }
        
        for wrong, correct in replacements.items():
            cleaned = cleaned.replace(wrong, correct)
        
        return cleaned
    
    def is_likely_plate(self, text):
        """Vérifie si le texte ressemble à une plaque"""
        cleaned = self.clean_plate_text(text)
        
        # Vérifier longueur
        if len(cleaned) < 6 or len(cleaned) > 12:
            return False
        
        # Vérifier mix lettres/chiffres
        has_letters = any(c.isalpha() for c in cleaned)
        has_digits = any(c.isdigit() for c in cleaned)
        
        if not (has_letters and has_digits):
            return False
        
        # Vérifier format français
        for pattern in PLATE_FORMATS['FR']:
            if re.match(pattern, cleaned):
                return True
        
        return False
    
    def process_results(self, ocr_results):
        """Traite les résultats OCR pour trouver les plaques"""
        plates = []
        
        for bbox, text, confidence in ocr_results:
            if self.is_likely_plate(text):
                cleaned_text = self.clean_plate_text(text)
                
                plates.append({
                    'bbox': bbox,
                    'text': cleaned_text,
                    'confidence': confidence,
                    'raw_text': text
                })
        
        # Trier par confiance (décroissant)
        plates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return plates