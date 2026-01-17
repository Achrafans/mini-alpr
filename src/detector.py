"""
Détection des plaques dans les images
"""

import cv2
import numpy as np
from .preprocessor import ImagePreprocessor

class PlateDetector:
    """Détecteur de plaques d'immatriculation"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.preprocessor = ImagePreprocessor()
        
    def find_plates(self, image):
        """
        Trouve les plaques dans une image
        Retourne une liste de régions d'intérêt (ROI)
        """
        plates = []
        
        # 1. Pré-traiter l'image
        processed = self.preprocessor.preprocess_for_ocr(image)
        
        # 2. Chercher des contours (méthode simple)
        # Pour un vrai projet, on utiliserait YOLO ou un modèle ML
        # Mais pour un mini-projet, cette méthode est suffisante
        
        # Seuillage
        _, thresh = cv2.threshold(processed, 0, 255, 
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Trouver les contours
        contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filtrer les contours
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Ignorer les trop petits/grands
            if area < 500 or area > 50000:
                continue
            
            # Rectangle englobant
            x, y, w, h = cv2.boundingRect(contour)
            
            # Ratio typique d'une plaque (~4.7:1)
            aspect_ratio = w / h
            if 3 < aspect_ratio < 6:
                plates.append({
                    'bbox': [x, y, x + w, y + h],
                    'confidence': 0.5,  # Estimation
                    'roi': image[y:y+h, x:x+w]
                })
        
        if self.debug:
            print(f"  Régions détectées: {len(plates)}")
        
        return plates
    
    def detect_with_easyocr(self, image):
        """
        Utilise EasyOCR pour détecter ET lire en une passe
        C'est la méthode la plus simple pour un mini-projet
        """
        # Cette méthode est implémentée dans OCREngine
        # On la garde ici pour compatibilité
        return []