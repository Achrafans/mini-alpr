"""
Gestionnaire d'Input/Output pour data/input et data/output
"""

import os
import cv2
import csv
from datetime import datetime
from constants import *

class IOManager:
    """Gère les opérations d'entrée/sortie de fichiers"""
    
    def __init__(self):
        self.create_directories()
    
    def create_directories(self):
        """Crée tous les dossiers nécessaires"""
        directories = [
            INPUT_DIR,
            OUTPUT_DIR,
            RESULTS_DIR,
            REPORTS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Dossier créé/vérifié: {os.path.relpath(directory, BASE_DIR)}")
    
    def get_relative_path(self, full_path):
        """Retourne le chemin relatif depuis le dossier du projet"""
        return os.path.relpath(full_path, BASE_DIR)
    
    def load_image(self, image_path):
        """Charge une image depuis le chemin donné"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Fichier non trouvé: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de lire l'image: {image_path}")
        
        return image
    
    def save_result_image(self, image, base_name, suffix="result"):
        """Sauvegarde une image de résultat"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{suffix}_{timestamp}.jpg"
        output_path = os.path.join(RESULTS_DIR, filename)
        
        cv2.imwrite(output_path, image)
        return output_path
    
    def save_plate_roi(self, image, bbox, base_name, plate_number):
        """Sauvegarde une région d'intérêt (plaque)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_plate_{plate_number}_{timestamp}.jpg"
        output_path = os.path.join(RESULTS_DIR, filename)
        
        # Extraire la région
        x_min = max(0, int(min(p[0] for p in bbox)) - 5)
        y_min = max(0, int(min(p[1] for p in bbox)) - 5)
        x_max = min(image.shape[1], int(max(p[0] for p in bbox)) + 5)
        y_max = min(image.shape[0], int(max(p[1] for p in bbox)) + 5)
        
        plate_roi = image[y_min:y_max, x_min:x_max]
        cv2.imwrite(output_path, plate_roi)
        
        return output_path
    
    def generate_text_report(self, input_path, plates):
        """Génère un rapport texte"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(REPORTS_DIR, f"{base_name}_report_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RAPPORT ALPR - Architecture Modulaire\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Fichier source: {os.path.basename(input_path)}\n")
            f.write(f"Chemin: {self.get_relative_path(input_path)}\n")
            f.write(f"Plaques détectées: {len(plates)}\n\n")
            
            if plates:
                f.write("DÉTAILS DES PLAQUES:\n")
                f.write("-"*40 + "\n")
                for i, plate in enumerate(plates, 1):
                    f.write(f"Plaque {i}:\n")
                    f.write(f"  Texte: {plate['text']}\n")
                    f.write(f"  Confiance: {plate['confidence']:.1%}\n")
                    f.write(f"  Format: {plate.get('format', 'Inconnu')}\n")
                    f.write("-"*40 + "\n")
            else:
                f.write("AUCUNE PLAQUE DÉTECTÉE\n")
        
        return report_file
    
    def generate_csv_report(self, input_path, plates):
        """Génère un rapport CSV"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(REPORTS_DIR, f"{base_name}_data_{timestamp}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # En-têtes
            writer.writerow([
                'Date', 'Fichier', 'ID_Plaque', 'Texte', 
                'Confiance', 'Format', 'X_min', 'Y_min', 'X_max', 'Y_max'
            ])
            
            # Données
            for i, plate in enumerate(plates, 1):
                bbox = plate.get('bbox', [(0,0), (0,0), (0,0), (0,0)])
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    os.path.basename(input_path),
                    i,
                    plate['text'],
                    f"{plate['confidence']:.1%}",
                    plate.get('format', 'Inconnu'),
                    min(x_coords),
                    min(y_coords),
                    max(x_coords),
                    max(y_coords)
                ])
        
        return csv_file
    
    def list_input_images(self):
        """Liste toutes les images dans data/input/"""
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            for file in os.listdir(INPUT_DIR):
                if file.lower().endswith(ext):
                    images.append(os.path.join(INPUT_DIR, file))
        
        return sorted(images)
    
    def create_test_image(self):
        """Crée une image de test si data/input/ est vide"""
        test_path = os.path.join(INPUT_DIR, "test_plate.jpg")
        
        if not os.path.exists(test_path):
            import numpy as np
            img = np.zeros((400, 800, 3), dtype=np.uint8)
            
            # Plaque française
            cv2.rectangle(img, (200, 150), (600, 250), (255, 255, 255), -1)
            cv2.rectangle(img, (200, 150), (600, 250), (0, 0, 0), 2)
            cv2.putText(img, "AB-123-CD", (250, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            
            # Voiture
            cv2.rectangle(img, (180, 130), (620, 270), (0, 100, 255), 2)
            
            cv2.imwrite(test_path, img)
            print(f"✅ Image test créée: {self.get_relative_path(test_path)}")
        
        return test_path