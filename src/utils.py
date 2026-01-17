"""
Fonctions utilitaires
"""

import cv2
import os
from datetime import datetime

def ensure_dir(directory):
    """Crée un dossier s'il n'existe pas"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_image(image_path):
    """Charge une image avec OpenCV"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image non trouvée: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de lire l'image: {image_path}")
    
    return image

def save_image(image, output_path):
    """Sauvegarde une image"""
    cv2.imwrite(output_path, image)
    print(f"  Image sauvegardée: {output_path}")

def draw_results(image, plates):
    """Dessine les résultats sur l'image"""
    result_image = image.copy()
    
    for plate in plates:
        # Récupérer les coordonnées
        bbox = plate['bbox']
        if len(bbox) == 4:  # [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, bbox)
            top_left = (x1, y1)
            bottom_right = (x2, y2)
        else:  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            points = [(int(p[0]), int(p[1])) for p in bbox]
            top_left = points[0]
            bottom_right = points[2]
        
        # Couleur selon la confiance
        color = (0, 255, 0) if plate['confidence'] > 0.7 else (0, 165, 255)
        
        # Dessiner rectangle
        cv2.rectangle(result_image, top_left, bottom_right, color, 2)
        
        # Ajouter texte
        label = f"{plate['text']} ({plate['confidence']:.1%})"
        cv2.putText(result_image, label, 
                   (top_left[0], top_left[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return result_image

def generate_filename(base_name, suffix="", extension="jpg"):
    """Génère un nom de fichier unique"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if suffix:
        return f"{base_name}_{suffix}_{timestamp}.{extension}"
    return f"{base_name}_{timestamp}.{extension}"