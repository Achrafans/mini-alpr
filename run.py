#!/usr/bin/env python3
"""
Script principal pour lancer le système ALPR
Usage: python run.py --image chemin/image.jpg
"""

import argparse
import sys
import os

# Ajouter le dossier src au chemin Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import ALPRSystem

def main():
    parser = argparse.ArgumentParser(description="Système ALPR - Reconnaissance de plaques")
    parser.add_argument('--image', type=str, required=True, help="Chemin vers l'image")
    parser.add_argument('--output', type=str, default='data/output/', help="Dossier de sortie")
    parser.add_argument('--debug', action='store_true', help="Mode debug")
    parser.add_argument('--batch', action='store_true', help="Traiter tout un dossier")
    
    args = parser.parse_args()
    
    # Initialiser le système
    print("=" * 50)
    print("🚗 SYSTÈME ALPR - Mini Projet")
    print("=" * 50)
    
    alpr = ALPRSystem(debug=args.debug)
    
    if args.batch:
        # Mode batch : traiter tout un dossier
        if not os.path.exists(args.image):
            print(f"❌ Erreur: Le dossier {args.image} n'existe pas")
            return
        
        print(f"📁 Traitement batch du dossier: {args.image}")
        results = alpr.batch_process(args.image, args.output)
        
        # Résumé
        total_plates = sum(len(r['plates']) for r in results if 'plates' in r)
        print(f"\n📊 RÉSUMÉ BATCH:")
        print(f"  Images traitées: {len(results)}")
        print(f"  Plaques détectées au total: {total_plates}")
        
    else:
        # Mode single : traiter une seule image
        if not os.path.exists(args.image):
            print(f"❌ Erreur: Le fichier {args.image} n'existe pas")
            print("\n📝 EXEMPLES D'UTILISATION:")
            print("  python run.py --image data/input/test1.jpg")
            print("  python run.py --image data/input/test1.jpg --debug")
            print("  python run.py --image data/input/ --batch --output results/")
            return
        
        print(f"📸 Traitement de: {args.image}")
        result = alpr.process_image(args.image, args.output)
        
        # Afficher les résultats
        print("\n" + "=" * 30)
        if result['success']:
            print("✅ RÉSULTATS:")
            for i, plate in enumerate(result['plates'], 1):
                print(f"  {i}. {plate['text']} (confiance: {plate['confidence']:.1%})")
        else:
            print("❌ Aucune plaque détectée")
        
        if 'processing_time' in result:
            print(f"\n⏱️  Temps de traitement: {result['processing_time']:.2f} secondes")
    
    print(f"\n💾 Résultats dans: {args.output}")
    print("=" * 50)

if __name__ == "__main__":
    main()