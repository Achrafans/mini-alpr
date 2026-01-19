"""
Pré-traitement des images pour l'OCR
"""

import cv2
import numpy as np

class ImagePreprocessor:
    """Pré-traite les images pour améliorer l'OCR"""
    
    @staticmethod
    def to_grayscale(image):
        """Convertit en niveaux de gris"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    @staticmethod
    def resize(image, max_width=1200):
        """Redimensionne l'image (conserve ratio)"""
        if image.shape[1] > max_width:
            ratio = max_width / image.shape[1]
            new_height = int(image.shape[0] * ratio)
            return cv2.resize(image, (max_width, new_height))
        return image
    
    @staticmethod
    def enhance_contrast(image):
        """Améliore le contraste (CLAHE)"""
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)
    
    @staticmethod
    def denoise(image):
        """Réduit le bruit"""
        return cv2.fastNlMeansDenoising(image, h=10)
    
    @staticmethod
    def sharpen(image):
        """Améliore la netteté"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    @staticmethod
    def preprocess_for_ocr(image):
        """Pipeline complet de pré-traitement pour OCR"""
        # 1. Redimensionner
        image = ImagePreprocessor.resize(image)
        
        # 2. Convertir en gris
        gray = ImagePreprocessor.to_grayscale(image)
        
        # 3. Améliorer contraste
        enhanced = ImagePreprocessor.enhance_contrast(gray)
        
        # 4. Réduire bruit
        denoised = ImagePreprocessor.denoise(enhanced)
        
        # 5. Améliorer netteté
        sharpened = ImagePreprocessor.sharpen(denoised)
        
        return sharpened