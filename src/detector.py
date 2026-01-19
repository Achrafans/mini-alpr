"""
Détecteur de plaques d'immatriculation
"""

import cv2
import numpy as np
from preprocessor import ImagePreprocessor

class PlateDetector:
    """Détecte les plaques dans les images"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.preprocessor = ImagePreprocessor()
        
        if debug:
            print("🔧 Détecteur de plaques initialisé")
    
    def find_plates(self, image):
        """Trouve les plaques dans une image"""
        # Pré-traiter l'image
        processed = self.preprocessor.preprocess_for_ocr(image)
        
        # Détection par contours (méthode simple)
        plates = self._detect_by_contours(processed, image)
        
        if self.debug:
            print(f"  📊 {len(plates)} région(s) potentielle(s) de plaque")
        
        return plates
    
    def _detect_by_contours(self, processed_image, original_image):
        """Détection par analyse de contours"""
        plates = []
        
        # Seuillage
        _, thresh = cv2.threshold(processed_image, 0, 255, 
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
            if 3.0 < aspect_ratio < 6.0:
                # ROI (Region of Interest)
                roi = original_image[y:y+h, x:x+w]
                
                plates.append({
                    'bbox': [x, y, x + w, y + h],
                    'roi': roi,
                    'confidence': 0.7,  # Estimation
                    'aspect_ratio': aspect_ratio,
                    'area': area
                })
        
        return plates