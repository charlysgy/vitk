"""
Advanced Usage Examples
======================

Ce fichier contient des exemples d'utilisation avancée des modules
pour des cas d'usage spécifiques.
"""

import numpy as np
from pathlib import Path

# Gestion des imports relatifs/absolus pour compatibilité
try:
    from .converters import load_medical_image, simple_numpy_to_vtk, numpy_to_vtk_volume
    from .visualization import InteractiveImageViewer
    from .utils import debug_array_info, calculate_intensity_stats, validate_volume_shape
except ImportError:
    # Fallback pour exécution directe
    from converters import load_medical_image, simple_numpy_to_vtk, numpy_to_vtk_volume
    from visualization import InteractiveImageViewer
    from utils import debug_array_info, calculate_intensity_stats, validate_volume_shape


def example_basic_comparison():
    """Exemple de base pour comparer deux images"""
    print("=== Exemple de comparaison de base ===")
    
    # Chargement des images
    image1_path = "./Data/case6_gre1.nrrd"
    image2_path = "./Data/case6_gre2.nrrd"
    
    _, array1 = load_medical_image(image1_path)
    _, array2 = load_medical_image(image2_path)
    
    # Validation
    validate_volume_shape(array1)
    validate_volume_shape(array2)
    
    # Analyse rapide
    debug_array_info(array1, "Image 1")
    debug_array_info(array2, "Image 2")
    
    # Visualisation
    viewer = InteractiveImageViewer(array1, array2)
    viewer.show()


def example_custom_analysis():
    """Exemple d'analyse personnalisée des volumes"""
    print("=== Exemple d'analyse personnalisée ===")
    
    # Chargement
    _, array1 = load_medical_image("./Data/case6_gre1.nrrd")
    _, array2 = load_medical_image("./Data/case6_gre2.nrrd")
    
    # Statistiques détaillées
    stats = calculate_intensity_stats(array1, array2)
    
    # Analyse des régions d'intérêt
    print("\n=== Analyse des régions centrales ===")
    
    # Extraire le centre de chaque volume
    center_z, center_y, center_x = np.array(array1.shape) // 2
    roi_size = 20  # Région de 40x40x40 voxels
    
    roi1 = array1[
        center_z-roi_size:center_z+roi_size,
        center_y-roi_size:center_y+roi_size,
        center_x-roi_size:center_x+roi_size
    ]
    
    roi2 = array2[
        center_z-roi_size:center_z+roi_size,
        center_y-roi_size:center_y+roi_size,
        center_x-roi_size:center_x+roi_size
    ]
    
    debug_array_info(roi1, "ROI Volume 1")
    debug_array_info(roi2, "ROI Volume 2")
    
    # Corrélation locale
    correlation = np.corrcoef(roi1.flatten(), roi2.flatten())[0, 1]
    print(f"Corrélation dans la ROI centrale: {correlation:.4f}")
    
    return stats


def example_slice_analysis():
    """Exemple d'analyse coupe par coupe"""
    print("=== Exemple d'analyse par coupe ===")
    
    _, array1 = load_medical_image("./Data/case6_gre1.nrrd")
    _, array2 = load_medical_image("./Data/case6_gre2.nrrd")
    
    print(f"Volume shape: {array1.shape}")
    
    # Analyse de quelques coupes axiales
    num_slices = array1.shape[0]
    slice_indices = [num_slices//4, num_slices//2, 3*num_slices//4]
    
    for i, slice_idx in enumerate(slice_indices):
        slice1 = array1[slice_idx, :, :]
        slice2 = array2[slice_idx, :, :]
        
        print(f"\n--- Coupe {slice_idx} ({i+1}/3) ---")
        print(f"Volume 1 - Min: {slice1.min():.2f}, Max: {slice1.max():.2f}, Mean: {slice1.mean():.2f}")
        print(f"Volume 2 - Min: {slice2.min():.2f}, Max: {slice2.max():.2f}, Mean: {slice2.mean():.2f}")
        
        # Différence
        diff = np.abs(slice2 - slice1)
        print(f"Différence abs - Max: {diff.max():.2f}, Mean: {diff.mean():.2f}")


def example_conversion_comparison():
    """Exemple de comparaison des méthodes de conversion"""
    print("=== Comparaison des méthodes de conversion ===")
    
    _, array1 = load_medical_image("./Data/case6_gre1.nrrd")
    
    # Test des deux méthodes de conversion
    vtk_simple = simple_numpy_to_vtk(array1)
    vtk_transposed = numpy_to_vtk_volume(array1)
    
    print("Conversion simple (ordre ITK):")
    print(f"  Dimensions: {vtk_simple.GetDimensions()}")
    print(f"  Spacing: {vtk_simple.GetSpacing()}")
    print(f"  Origin: {vtk_simple.GetOrigin()}")
    
    print("\nConversion avec transposition (ordre VTK):")
    print(f"  Dimensions: {vtk_transposed.GetDimensions()}")
    print(f"  Spacing: {vtk_transposed.GetSpacing()}")
    print(f"  Origin: {vtk_transposed.GetOrigin()}")
    
    # Comparaison des données
    from vtk.util import numpy_support
    
    vtk_array1 = numpy_support.vtk_to_numpy(vtk_simple.GetPointData().GetScalars())
    vtk_array2 = numpy_support.vtk_to_numpy(vtk_transposed.GetPointData().GetScalars())
    
    print(f"\nTaille des données VTK:")
    print(f"  Simple: {vtk_array1.size}")
    print(f"  Transposé: {vtk_array2.size}")
    print(f"  Original: {array1.size}")


def example_batch_processing():
    """Exemple de traitement par lot de plusieurs images"""
    print("=== Exemple de traitement par lot ===")
    
    data_dir = Path("./Data")
    image_files = list(data_dir.glob("*.nrrd"))
    
    print(f"Images trouvées: {len(image_files)}")
    
    results = {}
    
    for image_file in image_files:
        print(f"\nTraitement de: {image_file.name}")
        
        try:
            _, array = load_medical_image(str(image_file))
            validate_volume_shape(array)
            
            # Calcul des statistiques de base
            stats = {
                'shape': array.shape,
                'min': float(array.min()),
                'max': float(array.max()),
                'mean': float(array.mean()),
                'std': float(array.std()),
                'size_mb': array.nbytes / (1024 * 1024)
            }
            
            results[image_file.name] = stats
            
            print(f"  Shape: {stats['shape']}")
            print(f"  Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
            print(f"  Taille: {stats['size_mb']:.1f} MB")
            
        except Exception as e:
            print(f"  Erreur: {e}")
            results[image_file.name] = {'error': str(e)}
    
    return results


if __name__ == "__main__":
    print("Exemples d'utilisation avancée")
    print("Choisissez un exemple à exécuter:")
    print("1. Comparaison de base")
    print("2. Analyse personnalisée")
    print("3. Analyse par coupe")
    print("4. Comparaison des conversions")
    print("5. Traitement par lot")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    if choice == "1":
        example_basic_comparison()
    elif choice == "2":
        example_custom_analysis()
    elif choice == "3":
        example_slice_analysis()
    elif choice == "4":
        example_conversion_comparison()
    elif choice == "5":
        results = example_batch_processing()
        print("\nRésultats du traitement par lot:")
        for filename, stats in results.items():
            print(f"  {filename}: {stats}")
    else:
        print("Choix non valide")
