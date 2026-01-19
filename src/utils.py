"""
Fonctions utilitaires pour l'ALPR
"""

import cv2
import numpy as np
from datetime import datetime

def draw_results(image, plates):
    """Dessine les résultats sur l'image"""
    result_image = image.copy()
    
    for plate in plates:
        bbox = plate['bbox']
        
        # Convertir en points
        points = np.array(bbox, dtype=np.int32)
        
        # Couleur selon confiance
        confidence = plate['confidence']
        if confidence > 0.8:
            color = (0, 255, 0)    # Vert
        elif confidence > 0.6:
            color = (0, 200, 255)  # Orange
        else:
            color = (0, 0, 255)    # Rouge
        
        # Dessiner polygone
        cv2.polylines(result_image, [points], True, color, 2)
        
        # Texte
        label = f"{plate['text']} ({confidence:.0%})"
        x_min = int(min(p[0] for p in bbox))
        y_min = int(min(p[1] for p in bbox))
        
        # Fond pour le texte
        (text_width, text_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(result_image,
                     (x_min, y_min - text_height - 10),
                     (x_min + text_width, y_min),
                     color, -1)
        
        cv2.putText(result_image, label,
                   (x_min, y_min - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return result_image

def display_image(image, title="Résultat", timeout=3000):
    """Affiche une image temporairement"""
    cv2.imshow(title, image)
    cv2.waitKey(timeout)
    cv2.destroyAllWindows()

def get_timestamp():
    """Retourne un timestamp formaté"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def print_summary(input_path, plates, output_files):
    """Affiche un résumé des résultats"""
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DE L'ANALYSE")
    print("="*50)
    
    print(f"\n📁 Fichier: {input_path}")
    print(f"📅 Horodatage: {get_timestamp()}")
    
    if plates:
        print(f"\n✅ {len(plates)} plaque(s) détectée(s):")
        for plate in plates:
            print(f"  • {plate['text']} ({plate['confidence']:.1%})")
    else:
        print("\n⚠️  Aucune plaque détectée")
    
    if output_files:
        print(f"\n💾 Fichiers générés:")
        for key, path in output_files.items():
            if path and key != 'plates':
                print(f"  • {key}: {path}")