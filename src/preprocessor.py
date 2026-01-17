"""
Pré-traitement des images
"""

import cv2
import numpy as np

class ImagePreprocessor:
    """Classe pour le pré-traitement d'images"""
    
    @staticmethod
    def to_grayscale(image):
        """Convertit en niveaux de gris"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    @staticmethod
    def resize(image, max_width=800):
        """Redimensionne l'image (conserve ratio)"""
        if image.shape[1] > max_width:
            ratio = max_width / image.shape[1]
            new_height = int(image.shape[0] * ratio)
            return cv2.resize(image, (max_width, new_height))
        return image
    
    @staticmethod
    def enhance_contrast(image):
        """Améliore le contraste"""
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)
    
    @staticmethod
    def denoise(image):
        """Réduit le bruit"""
        return cv2.fastNlMeansDenoising(image, h=10)
    
    @staticmethod
    def preprocess_for_ocr(image):
        """Pipeline complet de pré-traitement pour OCR"""
        # 1. Convertir en gris si nécessaire
        gray = ImagePreprocessor.to_grayscale(image)
        
        # 2. Améliorer le contraste
        enhanced = ImagePreprocessor.enhance_contrast(gray)
        
        # 3. Réduire le bruit
        denoised = ImagePreprocessor.denoise(enhanced)
        
        return denoised
    
    @staticmethod
    def extract_plate_region(image, bbox):
        """Extrait une région de plaque"""
        if len(bbox) == 4:  # Format rectangle
            x1, y1, x2, y2 = map(int, bbox)
            return image[y1:y2, x1:x2]
        else:  # Format polygone
            # Trouver les limites
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            x1, x2 = int(min(xs)), int(max(xs))
            y1, y2 = int(min(ys)), int(max(ys))
            return image[y1:y2, x1:x2]