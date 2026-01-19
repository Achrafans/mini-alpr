#!/usr/bin/env python3
"""
ALPR SYSTEM avec Input/Output
Structure: data/input/ et data/output/
"""

import cv2
import numpy as np
import easyocr
import os
import sys
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse

class ALPRSystem:
    """Système complet ALPR avec gestion des fichiers"""
    
    def __init__(self, lang='fr', gpu=False):
        """Initialise le système ALPR"""
        print("="*70)
        print("🚗 ALPR SYSTEM - Version data/input data/output")
        print("="*70)
        
        # Définir les chemins
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(self.base_dir, 'data', 'input')
        self.output_dir = os.path.join(self.base_dir, 'data', 'output')
        self.results_dir = os.path.join(self.output_dir, 'results')
        self.reports_dir = os.path.join(self.output_dir, 'reports')
        
        # Créer les dossiers nécessaires
        self.create_folders()
        
        # Initialiser OCR
        print("\n🔧 Initialisation EasyOCR...")
        try:
            self.reader = easyocr.Reader([lang], gpu=gpu)
            print("✅ OCR prêt")
        except Exception as e:
            print(f"❌ Erreur OCR: {e}")
            raise
    
    def create_folders(self):
        """Crée la structure de dossiers data/"""
        folders = [
            self.input_dir,
            self.output_dir,
            self.results_dir,
            self.reports_dir
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Dossier créé/vérifié: {folder}")
    
    def get_relative_path(self, full_path):
        """Retourne le chemin relatif depuis le dossier du projet"""
        return os.path.relpath(full_path, self.base_dir)
    
    def process_single_image(self, image_path):
        """Traite une seule image"""
        print(f"\n📸 Traitement: {os.path.basename(image_path)}")
        print("-"*50)
        
        # Vérifier si le fichier existe
        if not os.path.exists(image_path):
            print(f"❌ Fichier non trouvé: {image_path}")
            return None
        
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Impossible de lire l'image: {image_path}")
            return None
        
        print(f"📏 Dimensions: {image.shape[1]}x{image.shape[0]}")
        
        # Redimensionner si trop grande (pour performance)
        if image.shape[1] > 1200:
            ratio = 1200 / image.shape[1]
            new_height = int(image.shape[0] * ratio)
            image = cv2.resize(image, (1200, new_height))
            print(f"📐 Redimensionné à: {image.shape[1]}x{image.shape[0]}")
        
        # Convertir pour OCR
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # OCR
        print("🔍 Analyse OCR en cours...")
        results = self.reader.readtext(rgb_image, paragraph=False)
        
        # Traiter les résultats
        plates = self.process_ocr_results(image, results)
        
        # Générer les fichiers de sortie
        output_files = self.generate_output(image_path, image, plates)
        
        # Afficher le résumé
        self.display_summary(image_path, plates, output_files)
        
        return output_files
    
    def process_ocr_results(self, image, ocr_results):
        """Traite les résultats OCR"""
        plates = []
        
        for i, (bbox, text, confidence) in enumerate(ocr_results):
            # Nettoyer le texte
            clean_text = self.clean_plate_text(text)
            
            # Vérifier si c'est une plaque
            if self.is_valid_plate(clean_text):
                plate_info = {
                    'id': i + 1,
                    'text': clean_text,
                    'confidence': confidence,
                    'original_text': text,
                    'bbox': bbox
                }
                plates.append(plate_info)
                
                # Dessiner sur l'image
                self.draw_plate_detection(image, bbox, clean_text, confidence)
                
                print(f"  🎯 Plaque {i+1}: {clean_text} ({confidence:.1%})")
        
        return plates
    
    def clean_plate_text(self, text):
        """Nettoie le texte de la plaque"""
        import re
        
        # Garder seulement alphanumérique et tirets
        cleaned = re.sub(r'[^\w\-]', '', text)
        cleaned = cleaned.upper()
        
        # Corrections OCR courantes
        corrections = {
            '0': 'O',
            '1': 'I',
            '5': 'S',
            '8': 'B',
            ' ': '',  # Enlever espaces
        }
        
        for wrong, right in corrections.items():
            cleaned = cleaned.replace(wrong, right)
        
        return cleaned
    
    def is_valid_plate(self, text):
        """Vérifie si le texte est une plaque valide"""
        if len(text) < 6 or len(text) > 12:
            return False
        
        # Doit contenir chiffres ET lettres
        has_digits = any(c.isdigit() for c in text)
        has_letters = any(c.isalpha() for c in text)
        
        if not (has_digits and has_letters):
            return False
        
        # Formats acceptés
        import re
        patterns = [
            r'^[A-Z]{2}-\d{3}-[A-Z]{2}$',  # AB-123-CD
            r'^[A-Z]{2}\d{3}[A-Z]{2}$',     # AB123CD
            r'^\d{1,4}[A-Z]{1,3}\d{2}$',    # Ancien format
        ]
        
        return any(re.match(p, text) for p in patterns)
    
    def draw_plate_detection(self, image, bbox, text, confidence):
        """Dessine la détection sur l'image"""
        # Convertir bbox en points
        points = np.array(bbox, dtype=np.int32)
        
        # Couleur selon la confiance
        if confidence > 0.8:
            color = (0, 255, 0)    # Vert
        elif confidence > 0.6:
            color = (0, 200, 255)  # Orange
        else:
            color = (0, 0, 255)    # Rouge
        
        # Dessiner le polygone
        cv2.polylines(image, [points], True, color, 3)
        
        # Ajouter le texte
        label = f"{text} ({confidence:.0%})"
        x_min = int(min(p[0] for p in bbox))
        y_min = int(min(p[1] for p in bbox))
        
        # Fond pour le texte
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(image, 
                     (x_min, y_min - text_height - 10),
                     (x_min + text_width, y_min),
                     color, -1)
        
        cv2.putText(image, label, 
                   (x_min, y_min - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def generate_output(self, input_path, image, plates):
        """Génère tous les fichiers de sortie dans data/output/"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_files = {
            'input': input_path,
            'timestamp': timestamp,
            'plates': plates
        }
        
        # 1. Image avec détections
        result_image = os.path.join(self.results_dir, f"{base_name}_result_{timestamp}.jpg")
        cv2.imwrite(result_image, image)
        output_files['result_image'] = result_image
        
        # 2. Image de chaque plaque (ROI)
        for i, plate in enumerate(plates):
            # Extraire la région de la plaque
            bbox = plate['bbox']
            x_coords = [int(p[0]) for p in bbox]
            y_coords = [int(p[1]) for p in bbox]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Extraire avec marge
            margin = 5
            plate_roi = image[
                max(0, y_min - margin):min(image.shape[0], y_max + margin),
                max(0, x_min - margin):min(image.shape[1], x_max + margin)
            ]
            
            plate_image = os.path.join(self.results_dir, f"{base_name}_plate_{i+1}_{timestamp}.jpg")
            cv2.imwrite(plate_image, plate_roi)
            plate['image_path'] = plate_image
        
        # 3. Rapport texte
        report_file = os.path.join(self.reports_dir, f"{base_name}_report_{timestamp}.txt")
        self.generate_text_report(report_file, input_path, plates, timestamp)
        output_files['report'] = report_file
        
        # 4. Rapport CSV (pour Excel)
        csv_file = os.path.join(self.reports_dir, f"{base_name}_data_{timestamp}.csv")
        self.generate_csv_report(csv_file, input_path, plates, timestamp)
        output_files['csv'] = csv_file
        
        return output_files
    
    def generate_text_report(self, filepath, input_path, plates, timestamp):
        """Génère un rapport texte"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RAPPORT ALPR - Reconnaissance de Plaques\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Date d'analyse: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Fichier source: {os.path.basename(input_path)}\n")
            f.write(f"Chemin complet: {self.get_relative_path(input_path)}\n")
            f.write(f"Identifiant analyse: {timestamp}\n")
            f.write("-"*60 + "\n\n")
            
            if plates:
                f.write(f"PLAQUES DÉTECTÉES: {len(plates)}\n\n")
                for plate in plates:
                    f.write(f"Plaque {plate['id']}:\n")
                    f.write(f"  Texte: {plate['text']}\n")
                    f.write(f"  Confiance: {plate['confidence']:.1%}\n")
                    f.write(f"  Texte original: {plate['original_text']}\n")
                    if 'image_path' in plate:
                        f.write(f"  Fichier image: {self.get_relative_path(plate['image_path'])}\n")
                    f.write("-"*40 + "\n")
            else:
                f.write("AUCUNE PLAQUE DÉTECTÉE\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("="*60 + "\n")
    
    def generate_csv_report(self, filepath, input_path, plates, timestamp):
        """Génère un rapport CSV (pour Excel)"""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # En-têtes
            writer.writerow([
                'Date', 'Fichier', 'ID_Plaque', 'Texte_Plaque',
                'Confiance', 'Texte_Original', 'Image_Plaque'
            ])
            
            # Données
            for plate in plates:
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    os.path.basename(input_path),
                    plate['id'],
                    plate['text'],
                    f"{plate['confidence']:.1%}",
                    plate['original_text'],
                    os.path.basename(plate.get('image_path', ''))
                ])
    
    def display_summary(self, input_path, plates, output_files):
        """Affiche un résumé à l'écran"""
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DE L'ANALYSE")
        print("="*50)
        
        print(f"\n📁 Fichier traité: {os.path.basename(input_path)}")
        print(f"📁 Emplacement: {self.get_relative_path(input_path)}")
        print(f"📅 Horodatage: {output_files['timestamp']}")
        
        if plates:
            print(f"\n✅ {len(plates)} plaque(s) détectée(s):")
            for plate in plates:
                print(f"  • {plate['text']} ({plate['confidence']:.1%})")
        else:
            print("\n⚠️  Aucune plaque détectée")
        
        print(f"\n💾 FICHIERS GÉNÉRÉS dans data/output/:")
        if 'result_image' in output_files:
            rel_path = self.get_relative_path(output_files['result_image'])
            print(f"  1. Image résultat: {rel_path}")
        
        if 'report' in output_files:
            rel_path = self.get_relative_path(output_files['report'])
            print(f"  2. Rapport texte: {rel_path}")
        
        if 'csv' in output_files:
            rel_path = self.get_relative_path(output_files['csv'])
            print(f"  3. Données CSV: {rel_path}")
        
        if plates:
            for i, plate in enumerate(plates):
                if 'image_path' in plate:
                    rel_path = self.get_relative_path(plate['image_path'])
                    print(f"  4.{i+1}. Image plaque {i+1}: {rel_path}")
        
        print(f"\n📁 Structure complète:")
        print(f"  • Entrée: {self.get_relative_path(self.input_dir)}/")
        print(f"  • Sortie: {self.get_relative_path(self.output_dir)}/")
        print(f"    ├── results/  (images)")
        print(f"    └── reports/  (textes)")

def select_image_gui():
    """Interface graphique pour sélectionner une image"""
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    file_path = filedialog.askopenfilename(
        title="Sélectionner une image",
        filetypes=[
            ("Images", "*.jpg *.jpeg *.png *.bmp"),
            ("Tous les fichiers", "*.*")
        ]
    )
    
    return file_path

def process_batch_folder(folder_path):
    """Traite toutes les images d'un dossier"""
    print(f"\n📁 TRAITEMENT BATCH: {folder_path}")
    print("-"*50)
    
    # Vérifier le dossier
    if not os.path.exists(folder_path):
        print(f"❌ Dossier non trouvé: {folder_path}")
        return
    
    # Lister les images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
    images = []
    
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            images.append(os.path.join(folder_path, file))
    
    if not images:
        print("❌ Aucune image trouvée dans le dossier")
        return
    
    print(f"📸 {len(images)} image(s) trouvée(s)")
    
    # Initialiser ALPR
    alpr = ALPRSystem()
    
    # Traiter chaque image
    all_results = []
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Traitement: {os.path.basename(image_path)}")
        
        try:
            results = alpr.process_single_image(image_path)
            if results:
                all_results.append(results)
        except Exception as e:
            print(f"❌ Erreur avec {os.path.basename(image_path)}: {e}")
    
    # Rapport final batch
    if all_results:
        print("\n" + "="*60)
        print("📊 RAPPORT FINAL BATCH")
        print("="*60)
        
        total_plates = sum(len(r['plates']) for r in all_results)
        total_images = len(all_results)
        
        print(f"\n📈 STATISTIQUES:")
        print(f"  • Images traitées: {total_images}/{len(images)}")
        print(f"  • Plaques détectées au total: {total_plates}")
        print(f"  • Taux de détection: {(total_images/len(images))*100:.1f}%")
        
        # Plaques uniques
        unique_plates = set()
        for result in all_results:
            for plate in result['plates']:
                unique_plates.add(plate['text'])
        
        print(f"  • Plaques uniques: {len(unique_plates)}")
        
        if unique_plates:
            print(f"\n  📋 Liste des plaques uniques:")
            for plate in sorted(unique_plates):
                print(f"    - {plate}")

def main():
    """Point d'entrée principal"""
    
    # Gestion des arguments
    parser = argparse.ArgumentParser(description="Système ALPR avec Input/Output")
    parser.add_argument('-i', '--input', help="Chemin de l'image à traiter")
    parser.add_argument('-d', '--directory', help="Dossier d'images à traiter (batch)")
    parser.add_argument('-g', '--gui', action='store_true', help="Ouvrir l'interface graphique")
    parser.add_argument('--data-input', action='store_true', help="Utiliser data/input par défaut")
    
    args = parser.parse_args()
    
    # Mode GUI
    if args.gui:
        print("🖼️  Mode interface graphique activé")
        image_path = select_image_gui()
        
        if image_path:
            print(f"📸 Image sélectionnée: {os.path.basename(image_path)}")
            alpr = ALPRSystem()
            alpr.process_single_image(image_path)
        else:
            print("❌ Aucune image sélectionnée")
        return
    
    # Mode batch
    if args.directory:
        process_batch_folder(args.directory)
        return
    
    # Mode single image
    image_path = None
    
    if args.input:
        # Chemin fourni en argument
        image_path = args.input
    elif args.data_input:
        # Utiliser data/input par défaut
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_input_dir = os.path.join(base_dir, 'data', 'input')
        
        # Chercher une image dans data/input
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            images = [f for f in os.listdir(data_input_dir) if f.lower().endswith(ext)]
            if images:
                image_path = os.path.join(data_input_dir, images[0])
                print(f"📸 Image trouvée dans data/input/: {images[0]}")
                break
        
        if not image_path:
            print("⚠️  Aucune image trouvée dans data/input/")
            print("   Création d'une image de test...")
            image_path = os.path.join(data_input_dir, "test_plate.jpg")
            img = np.zeros((400, 800, 3), dtype=np.uint8)
            cv2.putText(img, "AB-123-CD", (200, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.imwrite(image_path, img)
            print(f"✅ Image créée: data/input/test_plate.jpg")
    
    if not image_path:
        # Mode interactif
        print("\n📝 MODES D'UTILISATION:")
        print("  1. python alpr_io_data.py -i chemin/image.jpg")
        print("  2. python alpr_io_data.py -d dossier/images/")
        print("  3. python alpr_io_data.py -g (interface graphique)")
        print("  4. python alpr_io_data.py --data-input (utiliser data/input/)")
        print("  5. python alpr_io_data.py (mode interactif)")
        
        print("\n🎮 MODE INTERACTIF")
        print("-"*30)
        
        # Demander le chemin
        user_input = input("\nEntrez le chemin de l'image (ou 'data' pour data/input, 'dossier' pour batch): ").strip()
        
        if user_input.lower() == 'data':
            args.data_input = True
            main()  # Rappeler avec le flag
            return
        elif user_input.lower() == 'dossier':
            folder = input("Chemin du dossier: ").strip()
            process_batch_folder(folder)
            return
        elif user_input:
            image_path = user_input
        else:
            args.data_input = True
            main()  # Rappeler avec le flag
            return
    
    # Traiter l'image unique
    alpr = ALPRSystem()
    alpr.process_single_image(image_path)
    
    print("\n" + "="*70)
    print("✨ ALPR SYSTEM - TERMINÉ AVEC SUCCÈS!")
    print("="*70)

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour quitter...")