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
import itk
import vtk
import numpy as np
from vtk.util import numpy_support

# Import des modules locaux
try:
    # Imports en tant que package
    from .converters import load_medical_image, simple_numpy_to_vtk
    from .visualization import show_interactive_comparison
    from .utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, create_alignment_visual_report, register_vtk_images, numpy_to_itk_image, vtk_to_numpy_image
except ImportError:
    # Imports pour exécution directe
    from converters import load_medical_image, simple_numpy_to_vtk
    from visualization import show_interactive_comparison
    from utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, create_alignment_visual_report, register_vtk_images, numpy_to_itk_image, vtk_to_numpy_image
    import config


def main():
    """Point d'entrée principal de l'application"""
    print("=== Medical Image Comparison Tool ===")
    
    # Configuration des chemins
    data_dir = Path("./Data")
    image1_path = data_dir / config.DEFAULT_IMAGE1
    image2_path = data_dir / config.DEFAULT_IMAGE2
    
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
        
        # Vérification de l'alignement spatial
        print("\n" + "="*50)
        print("VÉRIFICATION DE L'ALIGNEMENT SPATIAL")
        print("="*50)
        
        alignment_info = check_volume_alignment(array1, array2, "case6_gre1", "case6_gre2")
        create_alignment_visual_report(array1, array2, alignment_info, "case6_gre1", "case6_gre2")
        
        # Test de conversion VTK
        print("\n" + "="*50)
        print("TEST DE CONVERSION VTK")
        print("="*50)
        
        vtk_image1 = simple_numpy_to_vtk(array1)
        vtk_image2 = simple_numpy_to_vtk(array2)
        
        print("✓ Conversion VTK réussie")
        print(f"  Volume 1 VTK - Dimensions: {vtk_image1.GetDimensions()}")
        print(f"  Volume 2 VTK - Dimensions: {vtk_image2.GetDimensions()}")
        
        # Recalage d'images
        print("\n" + "="*50)
        print("RECALAGE D'IMAGES")
        print("="*50)
        
        print("Recalage de l'image 2 sur l'image 1...")
        image3_vtk = register_vtk_images(vtk_image1, vtk_image2)
        print("✓ Recalage terminé")
        
        # Conversion de l'image recalée vers numpy pour l'affichage
        array3 = vtk_to_numpy_image(image3_vtk)
        print(f"  Image recalée - Dimensions: {array3.shape}")
        
        # Lancement de l'interface interactive avec l'image recalée
        print("\n" + "="*50)
        print("LANCEMENT DE L'INTERFACE INTERACTIVE")
        print("="*50)
        print("Affichage: Image 1 (référence) vs Image 2 (recalée)")
        
        show_interactive_comparison(array1, array3)

        print('=' * 50)
        print("Segmentation")
        print('=' * 50)

        vol1Itk = numpy_to_itk_image(array1, spacing=image1_itk.GetSpacing())
        vol2Itk = numpy_to_itk_image(array3, spacing=image2_itk.GetSpacing())

        otsu_filter1 = itk.OtsuThresholdImageFilter.New(vol1Itk)
        otsu_filter1.SetInsideValue(0)
        otsu_filter1.SetOutsideValue(1)
        otsu_filter1.Update()
        segmentation1 = otsu_filter1.GetOutput()

        otsu_filter2 = itk.OtsuThresholdImageFilter.New(vol2Itk)
        otsu_filter2.SetInsideValue(0)
        otsu_filter2.SetOutsideValue(1)
        otsu_filter2.Update()
        segmentation2 = otsu_filter2.GetOutput()

        seg1_np = itk.GetArrayFromImage(segmentation1)
        seg2_np = itk.GetArrayFromImage(segmentation2)

        show_interactive_comparison(seg1_np, seg2_np)

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
