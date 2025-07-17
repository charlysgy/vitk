#!/usr/bin/env python3
"""
Script de vérification d'alignement
==================================

Script dédié pour vérifier l'alignement spatial entre deux volumes médicaux.
Effectue une analyse complète sans lancer l'interface graphique.

Usage:
    python check_alignment.py
"""

import sys
from pathlib import Path

# Import des modules locaux
try:
    from .converters import load_medical_image
    from .utils import check_volume_alignment, create_alignment_visual_report
except ImportError:
    from converters import load_medical_image
    from utils import check_volume_alignment, create_alignment_visual_report


def main():
    """Point d'entrée pour la vérification d'alignement"""
    print("=== Vérification d'Alignement Spatial ===")
    
    # Configuration des chemins
    data_dir = Path("./Data")
    image1_path = data_dir / "case6_gre1.nrrd"
    image2_path = data_dir / "case6_gre2.nrrd"
    
    # Vérification de l'existence des fichiers
    if not image1_path.exists():
        print(f"Erreur: Fichier {image1_path} non trouvé")
        sys.exit(1)
    
    if not image2_path.exists():
        print(f"Erreur: Fichier {image2_path} non trouvé")
        sys.exit(1)
    
    try:
        # Chargement des images
        print(f"\nChargement des images...")
        print(f"  Image 1: {image1_path}")
        print(f"  Image 2: {image2_path}")
        
        image1_itk, array1 = load_medical_image(str(image1_path))
        image2_itk, array2 = load_medical_image(str(image2_path))
        
        print("✓ Images chargées avec succès")
        
        # Vérification de l'alignement spatial
        alignment_info = check_volume_alignment(array1, array2, "case6_gre1", "case6_gre2")
        create_alignment_visual_report(array1, array2, alignment_info, "case6_gre1", "case6_gre2")
        
        # Résumé final
        print(f"\n{'='*60}")
        print(f"RÉSUMÉ FINAL")
        print(f"{'='*60}")
        
        if alignment_info.get('is_well_aligned', False):
            print("✅ RÉSULTAT: Les volumes sont BIEN ALIGNÉS")
            print("   → Vous pouvez procéder à la comparaison avec confiance")
        else:
            print("❌ RÉSULTAT: Les volumes sont MAL ALIGNÉS")
            print("   → Un recalage spatial est recommandé avant la comparaison")
        
        print(f"\nPour une vérification visuelle interactive, exécutez:")
        print(f"   python main.py")
        print(f"   puis utilisez la touche 'a' pour analyser l'alignement à chaque position")
        
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
