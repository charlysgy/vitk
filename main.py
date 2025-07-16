"""
Medical Image Comparison Tool
============================

Script principal pour la comparaison interactive de volumes médicaux
utilisant ITK et VTK.

Usage:
    python main.py

Le script charge automatiquement les deux fichiers NRRD présents dans
le dossier Data/ et lance une interface interactive de comparaison.
"""

import os
import sys
from pathlib import Path

# Import des modules locaux
try:
    # Imports en tant que package
    from .converters import load_medical_image, simple_numpy_to_vtk
    from .visualization import show_interactive_comparison
    from .utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes
except ImportError:
    # Imports pour exécution directe
    from converters import load_medical_image, simple_numpy_to_vtk
    from visualization import show_interactive_comparison
    from utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes


def main():
    """Point d'entrée principal de l'application"""
    print("=== Medical Image Comparison Tool ===")
    
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
        
        # Analyse des données
        print("\n" + "="*50)
        print("ANALYSE DES DONNÉES")
        print("="*50)
        
        debug_array_info(array1, "Volume 1 (case6_gre1)")
        debug_array_info(array2, "Volume 2 (case6_gre2)")
        
        # Statistiques d'intensité
        stats = calculate_intensity_stats(array1, array2)
        print_intensity_stats(stats)
        
        # Comparaison des volumes
        compare_volumes(array1, array2, "case6_gre1", "case6_gre2")
        
        # Test de conversion VTK
        print("\n" + "="*50)
        print("TEST DE CONVERSION VTK")
        print("="*50)
        
        vtk_image1 = simple_numpy_to_vtk(array1)
        vtk_image2 = simple_numpy_to_vtk(array2)
        
        print("✓ Conversion VTK réussie")
        print(f"  Volume 1 VTK - Dimensions: {vtk_image1.GetDimensions()}")
        print(f"  Volume 2 VTK - Dimensions: {vtk_image2.GetDimensions()}")
        
        # Lancement de l'interface interactive
        print("\n" + "="*50)
        print("LANCEMENT DE L'INTERFACE INTERACTIVE")
        print("="*50)
        
        show_interactive_comparison(array1, array2)
        
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
