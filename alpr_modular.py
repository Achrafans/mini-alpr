#!/usr/bin/env python3
"""
ALPR avec architecture modulaire - Programme principal
"""

import os
import sys
import argparse

# Ajouter le dossier src au chemin Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from io_manager import IOManager
from detector import PlateDetector
from ocr_engine import OCREngine
from preprocessor import ImagePreprocessor
from utils import draw_results, display_image, print_summary

class ALPRModularSystem:
    """Système ALPR modulaire"""
    
    def __init__(self, debug=False):
        self.debug = debug
        
        print("="*70)
        print("🚗 ALPR SYSTEM - Architecture Modulaire")
        print("="*70)
        
        # Initialiser les composants
        self.io = IOManager()
        self.preprocessor = ImagePreprocessor()
        self.detector = PlateDetector(debug=debug)
        self.ocr = OCREngine(debug=debug)
        
        print("✅ Tous les composants sont initialisés")
    
    def process_image(self, image_path):
        """Traite une image complète"""
        try:
            # Charger l'image
            image = self.io.load_image(image_path)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            
            print(f"\n📸 Traitement: {base_name}")
            print(f"📏 Dimensions: {image.shape[1]}x{image.shape[0]}")
            
            # 1. Détecter les régions de plaque
            print("\n🔍 Détection des plaques...")
            plate_regions = self.detector.find_plates(image)
            
            all_plates = []
            
            # 2. Pour chaque région, faire l'OCR
            for i, region in enumerate(plate_regions, 1):
                print(f"\n  📋 Région {i}:")
                
                # OCR sur la ROI
                ocr_results = self.ocr.extract_text(region['roi'])
                
                # Traiter les résultats OCR
                plates = self.ocr.process_plates(ocr_results)
                
                # Ajuster les coordonnées des bbox
                for plate in plates:
                    # Convertir les coordonnées relatives en absolues
                    x_offset = region['bbox'][0]
                    y_offset = region['bbox'][1]
                    
                    adjusted_bbox = []
                    for point in plate['bbox']:
                        adjusted_bbox.append([
                            point[0] + x_offset,
                            point[1] + y_offset
                        ])
                    
                    plate['bbox'] = adjusted_bbox
                    all_plates.append(plate)
            
            # 3. Si aucune plaque détectée, essayer OCR sur toute l'image
            if not all_plates:
                print("\n⚠️  Aucune plaque détectée par région")
                print("🔍 Tentative OCR sur l'image complète...")
                
                ocr_results = self.ocr.extract_text(image)
                all_plates = self.ocr.process_plates(ocr_results)
            
            # 4. Générer les sorties
            output_files = {}
            
            if all_plates:
                # Dessiner résultats
                result_image = draw_results(image, all_plates)
                
                # Sauvegarder image résultat
                output_files['result_image'] = self.io.save_result_image(
                    result_image, base_name
                )
                
                # Sauvegarder chaque plaque
                for i, plate in enumerate(all_plates, 1):
                    plate_path = self.io.save_plate_roi(
                        image, plate['bbox'], base_name, i
                    )
                    plate['image_path'] = plate_path
                
                # Afficher l'image
                display_image(result_image, "ALPR Résultat")
            
            # 5. Générer rapports
            output_files['text_report'] = self.io.generate_text_report(
                image_path, all_plates
            )
            output_files['csv_report'] = self.io.generate_csv_report(
                image_path, all_plates
            )
            
            # 6. Afficher résumé
            print_summary(image_path, all_plates, output_files)
            
            return {
                'success': True,
                'plates': all_plates,
                'output_files': output_files
            }
            
        except Exception as e:
            print(f"\n❌ Erreur lors du traitement: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def process_batch(io_manager, system, folder_path):
    """Traite toutes les images d'un dossier"""
    print(f"\n📁 TRAITEMENT BATCH: {folder_path}")
    print("-"*50)
    
    images = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        for file in os.listdir(folder_path):
            if file.lower().endswith(ext):
                images.append(os.path.join(folder_path, file))
    
    if not images:
        print("❌ Aucune image trouvée")
        return
    
    print(f"📸 {len(images)} image(s) trouvée(s)")
    
    results = []
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] {os.path.basename(image_path)}")
        
        result = system.process_image(image_path)
        if result['success']:
            results.append(result)
    
    # Rapport batch
    if results:
        print("\n" + "="*60)
        print("📊 RAPPORT FINAL BATCH")
        print("="*60)
        
        total_plates = sum(len(r.get('plates', [])) for r in results)
        
        print(f"\n📈 STATISTIQUES:")
        print(f"  • Images traitées: {len(results)}/{len(images)}")
        print(f"  • Plaques détectées: {total_plates}")
        
        # Plaques uniques
        unique_plates = set()
        for result in results:
            for plate in result.get('plates', []):
                unique_plates.add(plate['text'])
        
        print(f"  • Plaques uniques: {len(unique_plates)}")

def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(description="ALPR System - Architecture Modulaire")
    parser.add_argument('-i', '--input', help="Chemin de l'image à traiter")
    parser.add_argument('-d', '--directory', help="Dossier d'images (batch)")
    parser.add_argument('--data-input', action='store_true', 
                       help="Utiliser data/input/ par défaut")
    parser.add_argument('--debug', action='store_true', 
                       help="Mode debug")
    
    args = parser.parse_args()
    
    # Initialiser le système
    system = ALPRModularSystem(debug=args.debug)
    io_manager = system.io
    
    # Déterminer le chemin de l'image
    image_path = None
    
    if args.data_input:
        # Utiliser data/input/
        images = io_manager.list_input_images()
        if images:
            image_path = images[0]
            print(f"📸 Utilisation de: {os.path.basename(image_path)}")
        else:
            print("⚠️  Aucune image dans data/input/, création d'une image test...")
            image_path = io_manager.create_test_image()
    
    elif args.input:
        # Chemin spécifique
        image_path = args.input
    
    elif args.directory:
        # Mode batch
        process_batch(io_manager, system, args.directory)
        return
    
    else:
        # Mode interactif
        print("\n📝 MODES D'UTILISATION:")
        print("  1. Traiter une image spécifique")
        print("  2. Traiter data/input/")
        print("  3. Traiter un dossier (batch)")
        print("  4. Quitter")
        
        choice = input("\nVotre choix (1-4): ").strip()
        
        if choice == '1':
            image_path = input("Chemin de l'image: ").strip()
        elif choice == '2':
            args.data_input = True
            main()  # Rappeler avec le flag
            return
        elif choice == '3':
            folder = input("Chemin du dossier: ").strip()
            process_batch(io_manager, system, folder)
            return
        elif choice == '4':
            return
        else:
            print("❌ Choix invalide")
            return
    
    # Traiter l'image
    if image_path:
        result = system.process_image(image_path)
        
        if result['success']:
            print("\n" + "="*70)
            print("✨ ALPR SYSTEM - TERMINÉ AVEC SUCCÈS!")
            print("="*70)
        else:
            print("\n❌ Le traitement a échoué")

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour quitter...")