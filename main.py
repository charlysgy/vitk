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
    from .utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, create_alignment_visual_report
except ImportError:
    # Imports pour exécution directe
    from converters import load_medical_image, simple_numpy_to_vtk
    from visualization import show_interactive_comparison
    from utils import debug_array_info, print_intensity_stats, calculate_intensity_stats, compare_volumes, check_volume_alignment, create_alignment_visual_report
    import config


def register_vtk_images(fixed_vtk_image, moving_vtk_image):
    """
    Perform image registration between two 3D images (vtkImageData).
    Returns the registered moving image as vtkImageData.
    """
    # Convert VTK images to numpy arrays
    def vtk_to_numpy_image(vtk_image):
        extent = vtk_image.GetExtent()
        dims = (extent[1] - extent[0] + 1, extent[3] - extent[2] + 1, extent[5] - extent[4] + 1)
        scalars = vtk_image.GetPointData().GetScalars()
        np_image = numpy_support.vtk_to_numpy(scalars)
        np_image = np_image.reshape(dims[::-1])  # z, y, x
        return np_image

    fixed_np = vtk_to_numpy_image(fixed_vtk_image)
    moving_np = vtk_to_numpy_image(moving_vtk_image)

    # Convert numpy arrays to ITK images
    fixed_itk = itk.image_view_from_array(fixed_np.astype(np.float32))
    moving_itk = itk.image_view_from_array(moving_np.astype(np.float32))

    # Perform registration using ITK (rigid)
    TransformType = itk.TranslationTransform[itk.D, 3]
    initial_transform = TransformType.New()

    MetricType = itk.MattesMutualInformationImageToImageMetricv4[
        type(fixed_itk), type(moving_itk)
    ]
    metric = MetricType.New()
    metric.SetNumberOfHistogramBins(50)

    OptimizerType = itk.RegularStepGradientDescentOptimizerv4[itk.D]
    optimizer = OptimizerType.New()
    optimizer.SetLearningRate(4.0)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(100)

    RegistrationType = itk.ImageRegistrationMethodv4[
        type(fixed_itk), type(moving_itk)
    ]
    registration = RegistrationType.New()
    registration.SetFixedImage(fixed_itk)
    registration.SetMovingImage(moving_itk)
    registration.SetInitialTransform(initial_transform)
    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)
    registration.SetShrinkFactorsPerLevel([4, 2, 1])
    registration.SetSmoothingSigmasPerLevel([2, 1, 0])

    registration.Update()
    final_transform = registration.GetTransform()

    # Resample moving image
    ResampleFilterType = itk.ResampleImageFilter[
        type(moving_itk), type(fixed_itk)
    ]
    resampler = ResampleFilterType.New()
    resampler.SetInput(moving_itk)
    resampler.SetTransform(final_transform)
    resampler.SetUseReferenceImage(True)
    resampler.SetReferenceImage(fixed_itk)
    resampler.SetInterpolator(
        itk.LinearInterpolateImageFunction[type(fixed_itk), itk.D].New()
    )
    resampler.Update()

    moved_itk = resampler.GetOutput()
    moved_np = itk.array_view_from_image(moved_itk)

    # Convert back to VTK image
    moved_flat = moved_np.astype(np.float32).ravel(order='C')
    vtk_moved = vtk.vtkImageData()
    vtk_moved.SetDimensions(moved_np.shape[::-1])
    vtk_moved.AllocateScalars(vtk.VTK_FLOAT, 1)
    vtk_array = numpy_support.numpy_to_vtk(moved_flat, deep=True, array_type=vtk.VTK_FLOAT)
    vtk_moved.GetPointData().SetScalars(vtk_array)

    return vtk_moved


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
        def vtk_to_numpy_image(vtk_image):
            extent = vtk_image.GetExtent()
            dims = (extent[1] - extent[0] + 1, extent[3] - extent[2] + 1, extent[5] - extent[4] + 1)
            scalars = vtk_image.GetPointData().GetScalars()
            np_image = numpy_support.vtk_to_numpy(scalars)
            np_image = np_image.reshape(dims[::-1])  # z, y, x
            return np_image
        
        array3 = vtk_to_numpy_image(image3_vtk)
        print(f"  Image recalée - Dimensions: {array3.shape}")
        
        # Lancement de l'interface interactive avec l'image recalée
        print("\n" + "="*50)
        print("LANCEMENT DE L'INTERFACE INTERACTIVE")
        print("="*50)
        print("Affichage: Image 1 (référence) vs Image 2 (recalée)")
        
        show_interactive_comparison(array1, array3)
        
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
