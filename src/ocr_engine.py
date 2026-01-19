"""
Moteur OCR basé sur EasyOCR
"""

import easyocr
import re
from constants import OCR_LANGUAGES, OCR_GPU, PLATE_FORMATS

class OCREngine:
    """Moteur de reconnaissance optique de caractères"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.reader = easyocr.Reader(
            OCR_LANGUAGES,
            gpu=OCR_GPU,
            model_storage_directory=None,
            download_enabled=True
        )
        
        if debug:
            print("🔧 OCR Engine initialisé (EasyOCR)")
    
    def extract_text(self, image):
        """Extrait le texte d'une image"""
        try:
            # EasyOCR attend du RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Lecture OCR
            results = self.reader.readtext(
                rgb_image,
                paragraph=False,
                detail=1
            )
            
            if self.debug:
                print(f"  📝 {len(results)} texte(s) détecté(s)")
            
            return results
            
        except Exception as e:
            if self.debug:
                print(f"  ❌ Erreur OCR: {e}")
            return []
    
    def process_plates(self, ocr_results):
        """Traite les résultats OCR pour trouver les plaques"""
        plates = []
        
        for bbox, text, confidence in ocr_results:
            # Nettoyer le texte
            cleaned_text = self._clean_text(text)
            
            # Vérifier si c'est une plaque
            plate_format = self._get_plate_format(cleaned_text)
            
            if plate_format:
                plates.append({
                    'text': cleaned_text,
                    'confidence': confidence,
                    'bbox': bbox,
                    'format': plate_format,
                    'raw_text': text
                })
                
                if self.debug:
                    print(f"  🎯 Plaque détectée: {cleaned_text} ({confidence:.1%})")
        
        # Trier par confiance
        plates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return plates
    
    def _clean_text(self, text):
        """Nettoie le texte de la plaque"""
        # Supprimer caractères spéciaux
        cleaned = re.sub(r'[^\w\-]', '', text)
        cleaned = cleaned.upper()
        
        # Corrections courantes
        corrections = {
            '0': 'O',
            '1': 'I',
            '5': 'S',
            '8': 'B'
        }
        
        for wrong, right in corrections.items():
            cleaned = cleaned.replace(wrong, right)
        
        return cleaned
    
    def _get_plate_format(self, text):
        """Détermine le format de la plaque"""
        for country, patterns in PLATE_FORMATS.items():
            for pattern in patterns:
                if re.match(pattern, text):
                    return f"{country}: {pattern}"
        
        # Vérifications de base
        if len(text) >= 6:
            has_letters = any(c.isalpha() for c in text)
            has_digits = any(c.isdigit() for c in text)
            
            if has_letters and has_digits:
                return "Format non standard"
        
        return None