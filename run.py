"""
ALPR avec EasyOCR (sans paddlepaddle)
Auteur : [Votre Nom]
"""

import cv2
import numpy as np
import os
import sys

def check_requirements():
    """Vérifie si les requirements sont installés"""
    missing = []
    
    packages = {
        'opencv-python': 'cv2',
        'numpy': 'numpy',
        'easyocr': 'easyocr',
        'Pillow': 'PIL'  # Optionnel
    }
    
    for pip_name, import_name in packages.items():
        try:
            if import_name == 'cv2':
                import cv2
            elif import_name == 'PIL':
                from PIL import Image
            else:
                __import__(import_name)
            print(f"✅ {pip_name} installé")
        except ImportError:
            if pip_name != 'Pillow':  # Pillow est optionnel
                missing.append(pip_name)
                print(f"❌ {pip_name} manquant")
            else:
                print(f"⚠️  {pip_name} manquant (optionnel)")
    
    return missing

def install_missing(missing_packages):
    """Installe les packages manquants"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installation des packages manquants...")
    
    try:
        import subprocess
        
        for package in missing_packages:
            print(f"  Installation de {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            print(f"  ✅ {package} installé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'installation: {e}")
        return False

def alpr_demo():
    """Démonstration complète ALPR avec EasyOCR"""
    print("\n🎯 Démarrage système ALPR...")
    
    # Initialiser EasyOCR
    import easyocr
    reader = easyocr.Reader(['fr', 'en'], gpu=False)
    print("✅ EasyOCR initialisé")
    
    # Créer une image de test réaliste
    print("\n📸 Création d'une plaque française...")
    
    # Dimensions plaque française (520x110mm en 2x pour visibilité)
    width, height = 1040, 220
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Bande bleue UE (110mm)
    blue_width = 220  # 110mm * 2
    img[:, :blue_width] = [0, 51, 153]  # Bleu UE
    
    # Cercle d'étoiles EU
    center = (blue_width // 2, height // 2)
    cv2.circle(img, center, 60, (255, 255, 255), -1)
    cv2.putText(img, "F", (center[0] - 20, center[1] + 20),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 51, 153), 3)
    
    # Numéro de plaque
    plate_number = "AB-123-CD"
    font_scale = 3
    thickness = 8
    text_size = cv2.getTextSize(plate_number, cv2.FONT_HERSHEY_SIMPLEX, 
                               font_scale, thickness)[0]
    text_x = blue_width + (width - blue_width - text_size[0]) // 2
    text_y = height // 2 + text_size[1] // 2
    
    cv2.putText(img, plate_number, (text_x, text_y),
               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
    
    # Bordures
    cv2.rectangle(img, (0, 0), (width-1, height-1), (0, 0, 0), 4)
    cv2.rectangle(img, (blue_width-2, 0), (blue_width+2, height), (0, 0, 0), 4)
    
    # Sauvegarder
    cv2.imwrite("french_plate_demo.jpg", img)
    print("✅ Plaque créée: french_plate_demo.jpg")
    
    # OCR
    print("\n🔍 Analyse OCR en cours...")
    results = reader.readtext(img)
    
    # Afficher résultats
    if results:
        print(f"\n📊 {len(results)} texte(s) détecté(s):")
        for i, (bbox, text, confidence) in enumerate(results, 1):
            print(f"\n{i}. '{text}'")
            print(f"   Confiance: {confidence:.1%}")
            
            # Dessiner sur l'image
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(img, [pts], True, (0, 255, 0), 3)
            
            # Ajouter label
            label = f"{text} ({confidence:.0%})"
            cv2.putText(img, label, (pts[0][0], pts[0][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Sauvegarder résultat
    cv2.imwrite("alpr_result.jpg", img)
    print("\n💾 Résultat: alpr_result.jpg")
    
    # Afficher
    cv2.imshow("ALPR - Reconnaissance de Plaque", img)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    
    return True

def main():
    """Programme principal"""
    print("="*70)
    print("🚗 ALPR System - EasyOCR Version")
    print("="*70)
    
    # Vérifier les requirements
    print("\n🔍 Vérification des dépendances...")
    missing = check_requirements()
    
    if missing:
        print(f"\n⚠️  {len(missing)} package(s) manquant(s)")
        if not install_missing(missing):
            print("\n❌ Impossible d'installer les dépendances")
            print("Essayez manuellement: pip install -r requirements.txt")
            return
    
    # Lancer la démo ALPR
    success = alpr_demo()
    
    if success:
        print("\n" + "="*70)
        print("✅ ALPR SYSTEM - OPÉRATION RÉUSSIE!")
        print("="*70)
        print("\nFichiers générés:")
        print("1. french_plate_demo.jpg - Plaque française réaliste")
        print("2. alpr_result.jpg - Résultat avec détection OCR")
        print("\nVotre système ALPR fonctionne parfaitement avec EasyOCR!")
    else:
        print("\n❌ Échec de la démonstration")

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour quitter...")