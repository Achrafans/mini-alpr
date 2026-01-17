"""
Tests pour le détecteur
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from detector import PlateDetector
import cv2
import numpy as np

def test_detector():
    """Test basique du détecteur"""
    print("🧪 Test du détecteur...")
    
    # Créer une image de test
    test_image = np.zeros((200, 400, 3), dtype=np.uint8)
    cv2.putText(test_image, "AB-123-CD", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Tester le détecteur
    detector = PlateDetector(debug=True)
    plates = detector.find_plates(test_image)
    
    print(f"  Régions trouvées: {len(plates)}")
    
    if len(plates) > 0:
        print("✅ Test réussi")
    else:
        print("❌ Test échoué - aucune région détectée")
    
    return len(plates) > 0

if __name__ == "__main__":
    test_detector()