"""
Système principal ALPR
"""

import cv2
import os
from datetime import datetime
from .detector import PlateDetector
from .ocr_engine import OCREngine
from .preprocessor import ImagePreprocessor
from .utils import load_image, save_image, draw_results, ensure_dir
from .constants import DEFAULT_OUTPUT_DIR

class ALPRSystem:
    """Système complet de reconnaissance de plaques"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.detector = PlateDetector(debug=debug)
        self.ocr = OCREngine(debug=debug)
        self.preprocessor = ImagePreprocessor()
        
        print("🚗 Système ALPR initialisé")
        if debug:
            print("  Mode debug activé")
    
    def process_image(self, image_path, output_dir=DEFAULT_OUTPUT_DIR):
        """
        Traite une image complète
        Retourne les résultats
        """
        results = {
            'success': False,
            'image_path': image_path,
            'plates': [],
            'processing_time': 0,
            'output_files': []
        }
        
        import time
        start_time = time.time()
        
        try:
            # 1. Charger l'image
            image = load_image(image_path)
            original_image = image.copy()
            
            # 2. Redimensionner si trop grande
            image = self.preprocessor.resize(image, max_width=1200)
            
            # 3. Utiliser EasyOCR pour détecter et lire
            ocr_results = self.ocr.extract_text(image)
            
            # 4. Filtrer pour ne garder que les plaques
            plates = self.ocr.process_results(ocr_results)
            
            # 5. Préparer les résultats
            results['plates'] = plates
            results['success'] = len(plates) > 0
            
            # 6. Sauvegarder les résultats
            if output_dir:
                self._save_results(original_image, plates, image_path, output_dir, results)
            
            # 7. Calculer le temps
            results['processing_time'] = time.time() - start_time
            
            if self.debug:
                print(f"\n📊 STATISTIQUES:")
                print(f"  Temps de traitement: {results['processing_time']:.2f}s")
                print(f"  Plaques trouvées: {len(plates)}")
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            results['error'] = str(e)
        
        return results
    
    def _save_results(self, image, plates, input_path, output_dir, results):
        """Sauvegarde tous les résultats"""
        ensure_dir(output_dir)
        
        # Nom de base basé sur l'image d'entrée
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Sauvegarder l'image avec annotations
        if plates:
            annotated_image = draw_results(image, plates)
            output_image_path = os.path.join(
                output_dir, 
                f"{base_name}_result_{timestamp}.jpg"
            )
            save_image(annotated_image, output_image_path)
            results['output_files'].append(output_image_path)
        
        # 2. Sauvegarder les plaques individuelles
        for i, plate in enumerate(plates):
            plate_roi = self.preprocessor.extract_plate_region(image, plate['bbox'])
            plate_path = os.path.join(
                output_dir,
                f"{base_name}_plate_{i+1}_{timestamp}.jpg"
            )
            save_image(plate_roi, plate_path)
            results['output_files'].append(plate_path)
        
        # 3. Sauvegarder un fichier texte avec les résultats
        txt_path = os.path.join(output_dir, f"{base_name}_results_{timestamp}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Résultats ALPR - {timestamp}\n")
            f.write(f"Image: {input_path}\n")
            f.write("=" * 50 + "\n\n")
            
            if plates:
                f.write(f"Plaques détectées: {len(plates)}\n\n")
                for i, plate in enumerate(plates, 1):
                    f.write(f"Plaque {i}:\n")
                    f.write(f"  Texte: {plate['text']}\n")
                    f.write(f"  Confiance: {plate['confidence']:.1%}\n")
                    f.write(f"  Texte brut: {plate['raw_text']}\n")
                    f.write("-" * 30 + "\n")
            else:
                f.write("Aucune plaque détectée\n")
            
            f.write(f"\nTemps de traitement: {results['processing_time']:.2f} secondes\n")
        
        results['output_files'].append(txt_path)
        print(f"  Fichier texte: {txt_path}")
    
    def batch_process(self, input_dir, output_dir=DEFAULT_OUTPUT_DIR):
        """Traite toutes les images d'un dossier"""
        import glob
        
        image_files = glob.glob(os.path.join(input_dir, "*.jpg")) + \
                     glob.glob(os.path.join(input_dir, "*.png")) + \
                     glob.glob(os.path.join(input_dir, "*.jpeg"))
        
        print(f"📁 Traitement batch: {len(image_files)} images")
        
        all_results = []
        for image_file in image_files:
            print(f"\n➡️  Traitement: {os.path.basename(image_file)}")
            result = self.process_image(image_file, output_dir)
            all_results.append(result)
        
        return all_results


# Fonction pour une utilisation simple
def simple_demo():
    """Démonstration simple"""
    print("=" * 50)
    print("DÉMONSTRATION ALPR - Mini Projet")
    print("=" * 50)
    
    # Créer une instance
    alpr = ALPRSystem(debug=True)
    
    # Traiter une image d'exemple
    test_image = "data/input/test_plate.jpg"
    
    if os.path.exists(test_image):
        result = alpr.process_image(test_image)
        
        if result['success']:
            print("\n🎉 DÉMO RÉUSSIE !")
            print(f"Plaques trouvées: {len(result['plates'])}")
            for plate in result['plates']:
                print(f"  - {plate['text']} ({plate['confidence']:.1%})")
        else:
            print("\n⚠️  Aucune plaque détectée dans l'image de test")
    else:
        print(f"\n❌ Image de test non trouvée: {test_image}")
        print("Placez une image nommée 'test_plate.jpg' dans data/input/")

if __name__ == "__main__":
    # Si on exécute directement ce fichier
    simple_demo()