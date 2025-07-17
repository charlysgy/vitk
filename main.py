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
    from .utils import postprocess_segmentation, numpy_to_itk_image, debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, register_vtk_images, semi_automatic_segmentation, vtk_to_numpy_image, automatic_segmentation, preprocess_volume, region_growing_segmentation
except ImportError:
    # Imports pour exécution directe
    from converters import load_medical_image, simple_numpy_to_vtk
    from visualization import show_interactive_comparison
    from utils import postprocess_segmentation, numpy_to_itk_image, debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, register_vtk_images, semi_automatic_segmentation, vtk_to_numpy_image, automatic_segmentation, preprocess_volume, region_growing_segmentation
    import config

def show_3d_tumor_change(seg1_np, seg2_np, scan_np):
    """
    Affiche le crâne issu du scan (gris), la tumeur 1 (bleu) et la tumeur 2 (rouge) dans la même scène 3D.
    """
    import vtk

    def numpy_to_vtk_mask(np_mask):
        dims = np_mask.shape[::-1]
        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dims)
        vtk_img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        flat = np_mask.astype(np.uint8).ravel(order='C')
        vtk_arr = numpy_support.numpy_to_vtk(flat, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        vtk_img.GetPointData().SetScalars(vtk_arr)
        return vtk_img

    def numpy_to_vtk_image(np_img):
        dims = np_img.shape[::-1]
        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dims)
        vtk_img.AllocateScalars(vtk.VTK_FLOAT, 1)
        flat = np_img.astype(np.float32).ravel(order='C')
        vtk_arr = numpy_support.numpy_to_vtk(flat, deep=True, array_type=vtk.VTK_FLOAT)
        vtk_img.GetPointData().SetScalars(vtk_arr)
        return vtk_img

    def make_surface(vtk_img, color, opacity=0.4):
        contour = vtk.vtkMarchingCubes()
        contour.SetInputData(vtk_img)
        contour.SetValue(0, 0.5)
        contour.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(contour.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetDiffuseColor(color)
        actor.GetProperty().SetDiffuse(1.0)
        actor.GetProperty().SetAmbient(0.3)
        actor.GetProperty().SetSpecular(0.0)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetInterpolationToPhong()
        return actor

    # --- Génération de la surface du crâne ---
    # On suppose que les valeurs élevées correspondent à l'os (par exemple > 200)
    skull_threshold = 200  # À ajuster selon ton scanner
    skull_mask = (scan_np > skull_threshold).astype(np.uint8)
    vtk_skull = numpy_to_vtk_mask(skull_mask)
    actor_skull = make_surface(vtk_skull, (0.8, 0.8, 0.8), 0.05)  # Gris translucide

    # --- Génération des surfaces des tumeurs ---
    vtk1 = numpy_to_vtk_mask(seg1_np)
    vtk2 = numpy_to_vtk_mask(seg2_np)
    actor1 = make_surface(vtk1, (0, 0, 1), 0.7)  # Bleu
    actor2 = make_surface(vtk2, (1, 0, 0), 0.7)  # Rouge

    # --- Affichage ---
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor_skull)
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(900, 900)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    render_window.Render()
    interactor.Start()

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

        # PRETRAITEMENT
        preprocessed_volume1_np = preprocess_volume(array1)
        preprocessed_volume2_np = preprocess_volume(array3)
        preprocessed_volume1_itk = numpy_to_itk_image(preprocessed_volume1_np)
        preprocessed_volume2_itk = numpy_to_itk_image(preprocessed_volume2_np)

        # SEGEMENTATION
        seg1_np = region_growing_segmentation(preprocessed_volume1_itk, (85, 70, 50))
        seg2_np = region_growing_segmentation(preprocessed_volume2_itk, (85, 70, 50))

        # POST-TRAITEMENT\
        final1_np = postprocess_segmentation(seg1_np)
        final2_np = postprocess_segmentation(seg2_np)

        show_interactive_comparison(final1_np, final2_np)

        print('=' * 50)
        print("Visualisation 3D des changements de la tumeur")
        print('=' * 50)
        show_3d_tumor_change(final1_np, final2_np, array1)

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
