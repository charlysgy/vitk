"""
Utils Module
============

Ce module contient les fonctions utilitaires pour le débogage,
la validation et l'analyse des données d'images.

Fonctions:
    - debug_array_info: Affiche des informations détaillées sur un array
    - validate_volume_shape: Valide la forme d'un volume 3D
    - calculate_intensity_stats: Calcule les statistiques d'intensité
"""

import itk
import vtk
import numpy as np
from vtk.util import numpy_support

import numpy as np
import scipy.ndimage as ndi
from scipy.ndimage import (
    binary_opening,
    binary_closing,
    gaussian_filter,
    label,
    binary_fill_holes
)

def postprocess_segmentation(mask: np.ndarray,
                              min_size: int = 100,
                              apply_smoothing: bool = True,
                              smoothing_sigma: float = 1.0) -> np.ndarray:
    """
    Applique un post-traitement morphologique et un lissage à un masque binaire.

    Args:
        mask (np.ndarray): Masque binaire 3D (0/1), shape (Z, Y, X)
        min_size (int): Seuil minimal de taille (en voxels) pour conserver une région
        apply_smoothing (bool): Appliquer un lissage par filtre gaussien
        smoothing_sigma (float): Sigma du filtre gaussien

    Returns:
        np.ndarray: Masque post-traité (0/1)
    """
    # S'assurer que c’est bien un masque binaire
    mask = (mask > 0).astype(np.uint8)

    # Remplissage des trous internes
    mask = binary_fill_holes(mask).astype(np.uint8)

    # Morphologie : ouverture (nettoyage bruit), puis fermeture (remplit petits trous)
    mask = binary_opening(mask, structure=np.ones((3, 3, 3))).astype(np.uint8)
    mask = binary_closing(mask, structure=np.ones((3, 3, 3))).astype(np.uint8)

    # Supprimer les petits objets
    labeled, num = label(mask)
    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0  # ignorer le fond
    mask_clean = np.zeros_like(mask)

    for i, size in enumerate(sizes):
        if size >= min_size:
            mask_clean[labeled == i] = 1

    # Lissage optionnel des contours
    if apply_smoothing:
        smoothed = gaussian_filter(mask_clean.astype(np.float32), sigma=smoothing_sigma)
        mask_clean = (smoothed > 0.5).astype(np.uint8)

    return mask_clean

def region_growing_segmentation(itk_image, seed: tuple[int, int, int], multiplier=2.5, iterations=5) -> np.ndarray:
    """
    Segmentation par croissance de région (ITK.ConfidenceConnected).
    """
    filter = itk.ConfidenceConnectedImageFilter.New(itk_image)
    filter.SetSeed(seed)
    filter.SetMultiplier(multiplier)
    filter.SetNumberOfIterations(iterations)
    filter.SetInitialNeighborhoodRadius(1)
    filter.SetReplaceValue(1)
    filter.Update()

    segmentation = filter.GetOutput()
    return itk.GetArrayFromImage(segmentation)

def preprocess_volume(volume: np.ndarray, normalize: bool = True, apply_smoothing: bool = True) -> np.ndarray:
    """
    Applique un prétraitement standard à un volume médical 3D.
    
    Args:
        volume (np.ndarray): Volume 3D d'intensité float32 (par exemple IRM, CT), shape (Z, Y, X)
        normalize (bool): Appliquer la normalisation des intensités (0–1)
        apply_smoothing (bool): Appliquer un floutage gaussien léger pour réduire le bruit
        
    Returns:
        np.ndarray: Volume prétraité (même shape)
    """
    # Vérification du type
    if not isinstance(volume, np.ndarray) or volume.ndim != 3:
        raise ValueError("Le volume doit être un numpy.ndarray 3D (Z, Y, X)")

    # Conversion en float32 pour compatibilité avec ITK, segmentation, etc.
    volume = volume.astype(np.float32)

    # Suppression des valeurs aberrantes (clipping à 1e et 99e percentile)
    p1, p99 = np.percentile(volume, [1, 99])
    volume = np.clip(volume, p1, p99)

    # Normalisation optionnelle (0-1)
    if normalize:
        vmin, vmax = volume.min(), volume.max()
        if vmax > vmin:
            volume = (volume - vmin) / (vmax - vmin)
        else:
            volume = np.zeros_like(volume)

    # Floutage optionnel (gaussien isotrope sigma=1)
    if apply_smoothing:
        volume = ndi.gaussian_filter(volume, sigma=1)

    return volume


def automatic_segmentation(image1_np, image2_np, image1_itk, image2_itk):
    """
    Effectue une segmentation automatique d'une image en utilisant un seuil.
    
    Args:
        image (numpy.ndarray): Image à segmenter
        threshold (float): Seuil pour la segmentation
        
    Returns:
        numpy.ndarray: Image segmentée
    """
    # Appliquer un seuil pour la segmentation
    vol1Itk = numpy_to_itk_image(image1_np, spacing=image1_itk.GetSpacing())
    vol2Itk = numpy_to_itk_image(image2_np, spacing=image2_itk.GetSpacing())

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

    return seg1_np, seg2_np

def semi_automatic_segmentation(image1_np, image2_np, image1_itk, image2_itk, threshold1, threshold2):
    """
    Effectue une segmentation semi-automatique à partir de deux images
    en utilisant un seuil défini manuellement.

    Args:
        image1_np (np.ndarray): Premier volume (référence)
        image2_np (np.ndarray): Deuxième volume (recalé)
        image1_itk (itk.Image): Version ITK de image1_np
        image2_itk (itk.Image): Version ITK de image2_np
        threshold1 (float): Seuil de segmentation pour image1
        threshold2 (float): Seuil de segmentation pour image2

    Returns:
        tuple: (segmentation1_np, segmentation2_np), deux tableaux numpy binaires
    """
    # Conversion vers ITK
    vol1Itk = numpy_to_itk_image(image1_np, spacing=image1_itk.GetSpacing())
    vol2Itk = numpy_to_itk_image(image2_np, spacing=image2_itk.GetSpacing())

    # Seuillage manuel pour image 1
    thresh_filter1 = itk.BinaryThresholdImageFilter.New(vol1Itk)
    thresh_filter1.SetLowerThreshold(threshold1)
    thresh_filter1.SetUpperThreshold(255)
    thresh_filter1.SetInsideValue(1)
    thresh_filter1.SetOutsideValue(0)
    thresh_filter1.Update()
    segmentation1 = thresh_filter1.GetOutput()

    # Seuillage manuel pour image 2
    thresh_filter2 = itk.BinaryThresholdImageFilter.New(vol2Itk)
    thresh_filter2.SetLowerThreshold(threshold2)
    thresh_filter2.SetUpperThreshold(255)
    thresh_filter2.SetInsideValue(1)
    thresh_filter2.SetOutsideValue(0)
    thresh_filter2.Update()
    segmentation2 = thresh_filter2.GetOutput()

    # Conversion vers numpy
    seg1_np = itk.GetArrayFromImage(segmentation1)
    seg2_np = itk.GetArrayFromImage(segmentation2)

    return seg1_np, seg2_np


def vtk_to_numpy_image(vtk_image):
            extent = vtk_image.GetExtent()
            dims = (extent[1] - extent[0] + 1, extent[3] - extent[2] + 1, extent[5] - extent[4] + 1)
            scalars = vtk_image.GetPointData().GetScalars()
            np_image = numpy_support.vtk_to_numpy(scalars)
            np_image = np_image.reshape(dims[::-1])  # z, y, x
            return np_image

def numpy_to_itk_image(array, spacing=(1.0, 1.0, 1.0)):
    image = itk.image_from_array(array.astype(np.float32))
    image.SetSpacing(spacing)
    return image

def debug_array_info(array, name="Array"):
    """
    Affiche des informations détaillées de débogage sur un array NumPy.
    
    Args:
        array (numpy.ndarray): Array à analyser
        name (str): Nom descriptif pour l'affichage
    """
    print(f"\n=== {name} ===")
    print(f"Shape: {array.shape}")
    print(f"Dtype: {array.dtype}")
    print(f"Min: {array.min():.2f}, Max: {array.max():.2f}")
    print(f"Mean: {array.mean():.2f}, Std: {array.std():.2f}")
    print(f"Non-zero count: {np.count_nonzero(array)}/{array.size}")
    
    # Informations additionnelles pour les volumes 3D
    if len(array.shape) == 3:
        print(f"Volume size: {array.shape[0]} x {array.shape[1]} x {array.shape[2]}")
        print(f"Total voxels: {array.size:,}")
        
        # Test de coupe centrale
        mid_slice = array[array.shape[0]//2, :, :]
        print(f"Coupe centrale (axiale) - Min: {mid_slice.min():.2f}, Max: {mid_slice.max():.2f}")


def validate_volume_shape(volume, expected_dims=3):
    """
    Valide qu'un volume a la forme attendue.
    
    Args:
        volume (numpy.ndarray): Volume à valider
        expected_dims (int): Nombre de dimensions attendu
        
    Returns:
        bool: True si la forme est valide
        
    Raises:
        ValueError: Si la forme n'est pas valide
    """
    if not isinstance(volume, np.ndarray):
        raise ValueError("Le volume doit être un array NumPy")
    
    if len(volume.shape) != expected_dims:
        raise ValueError(f"Volume doit avoir {expected_dims} dimensions, "
                        f"mais a {len(volume.shape)} dimensions")
    
    if expected_dims == 3:
        if any(dim <= 0 for dim in volume.shape):
            raise ValueError("Toutes les dimensions doivent être positives")
            
        if volume.size == 0:
            raise ValueError("Le volume ne peut pas être vide")
    
    return True


def calculate_intensity_stats(volume1, volume2=None):
    """
    Calcule les statistiques d'intensité pour un ou deux volumes.
    
    Args:
        volume1 (numpy.ndarray): Premier volume
        volume2 (numpy.ndarray, optional): Deuxième volume pour comparaison
        
    Returns:
        dict: Dictionnaire contenant les statistiques calculées
    """
    stats = {}
    
    # Statistiques pour le volume 1
    stats['volume1'] = {
        'min': float(volume1.min()),
        'max': float(volume1.max()),
        'mean': float(volume1.mean()),
        'std': float(volume1.std()),
        'percentile_1': float(np.percentile(volume1, 1)),
        'percentile_99': float(np.percentile(volume1, 99))
    }
    
    # Si un deuxième volume est fourni
    if volume2 is not None:
        stats['volume2'] = {
            'min': float(volume2.min()),
            'max': float(volume2.max()),
            'mean': float(volume2.mean()),
            'std': float(volume2.std()),
            'percentile_1': float(np.percentile(volume2, 1)),
            'percentile_99': float(np.percentile(volume2, 99))
        }
        
        # Statistiques combinées pour les niveaux d'affichage
        combined = np.concatenate([volume1.flatten(), volume2.flatten()])
        non_zero = combined[combined > 0]
        
        if len(non_zero) > 0:
            stats['combined'] = {
                'min_intensity': float(np.percentile(non_zero, 1)),
                'max_intensity': float(np.percentile(non_zero, 99)),
            }
        else:
            stats['combined'] = {
                'min_intensity': float(combined.min()),
                'max_intensity': float(combined.max()),
            }
            
        # Calcul de window/level pour l'affichage
        window = stats['combined']['max_intensity'] - stats['combined']['min_intensity']
        level = (stats['combined']['max_intensity'] + stats['combined']['min_intensity']) / 2
        
        stats['display'] = {
            'window': window,
            'level': level
        }
    
    return stats


def print_intensity_stats(stats):
    """
    Affiche les statistiques d'intensité de manière formatée.
    
    Args:
        stats (dict): Statistiques retournées par calculate_intensity_stats
    """
    print("\n=== Statistiques d'Intensité ===")
    
    for volume_name, volume_stats in stats.items():
        if volume_name in ['volume1', 'volume2']:
            print(f"\n{volume_name.upper()}:")
            print(f"  Min: {volume_stats['min']:.2f}")
            print(f"  Max: {volume_stats['max']:.2f}")
            print(f"  Moyenne: {volume_stats['mean']:.2f}")
            print(f"  Écart-type: {volume_stats['std']:.2f}")
            print(f"  Percentiles 1-99%: {volume_stats['percentile_1']:.2f} - {volume_stats['percentile_99']:.2f}")
    
    if 'display' in stats:
        print(f"\nPARAMÈTRES D'AFFICHAGE:")
        print(f"  Window: {stats['display']['window']:.2f}")
        print(f"  Level: {stats['display']['level']:.2f}")


def compare_volumes(volume1, volume2, name1="Volume 1", name2="Volume 2"):
    """
    Compare deux volumes et affiche les différences.
    
    Args:
        volume1, volume2 (numpy.ndarray): Volumes à comparer
        name1, name2 (str): Noms des volumes pour l'affichage
    """
    print(f"\n=== Comparaison {name1} vs {name2} ===")
    
    # Vérification des formes
    if volume1.shape != volume2.shape:
        print(f"ATTENTION: Formes différentes!")
        print(f"  {name1}: {volume1.shape}")
        print(f"  {name2}: {volume2.shape}")
        return
    
    # Calcul des différences
    diff = volume2 - volume1
    abs_diff = np.abs(diff)
    
    print(f"Forme identique: {volume1.shape}")
    print(f"Différence moyenne: {diff.mean():.4f}")
    print(f"Différence absolue moyenne: {abs_diff.mean():.4f}")
    print(f"Différence max: {abs_diff.max():.4f}")
    print(f"Corrélation: {np.corrcoef(volume1.flatten(), volume2.flatten())[0,1]:.4f}")


def check_volume_alignment(volume1, volume2, name1="Volume 1", name2="Volume 2"):
    """
    Vérifie l'alignement spatial entre deux volumes médicaux.
    
    Args:
        volume1, volume2 (numpy.ndarray): Volumes à comparer
        name1, name2 (str): Noms des volumes pour l'affichage
        
    Returns:
        dict: Dictionnaire contenant les métriques d'alignement
    """
    print(f"\n{'='*60}")
    print(f"VÉRIFICATION DE L'ALIGNEMENT - {name1} vs {name2}")
    print(f"{'='*60}")
    
    alignment_info = {}
    
    # 1. Vérification des dimensions
    print(f"\n1. VÉRIFICATION DES DIMENSIONS:")
    print(f"   {name1}: {volume1.shape}")
    print(f"   {name2}: {volume2.shape}")
    
    if volume1.shape != volume2.shape:
        print(f"   ❌ ATTENTION: Les volumes ont des dimensions différentes!")
        print(f"   → Recalage spatial nécessaire")
        alignment_info['dimensions_match'] = False
        alignment_info['needs_registration'] = True
        return alignment_info
    else:
        print(f"   ✅ Dimensions identiques")
        alignment_info['dimensions_match'] = True
    
    # 2. Analyse des centres de masse
    print(f"\n2. ANALYSE DES CENTRES DE MASSE:")
    com1 = calculate_center_of_mass(volume1)
    com2 = calculate_center_of_mass(volume2)
    
    print(f"   {name1}: ({com1[0]:.2f}, {com1[1]:.2f}, {com1[2]:.2f})")
    print(f"   {name2}: ({com2[0]:.2f}, {com2[1]:.2f}, {com2[2]:.2f})")
    
    com_distance = np.sqrt(np.sum((np.array(com1) - np.array(com2))**2))
    print(f"   Distance entre centres: {com_distance:.2f} voxels")
    
    alignment_info['center_of_mass'] = {
        'volume1': com1,
        'volume2': com2,
        'distance': com_distance
    }
    
    # 3. Analyse de corrélation spatiale par tranches
    print(f"\n3. CORRÉLATION SPATIALE PAR TRANCHES:")
    correlations = analyze_slice_correlations(volume1, volume2)
    
    print(f"   Axiale   - Moyenne: {correlations['axial']['mean']:.3f}, Min: {correlations['axial']['min']:.3f}")
    print(f"   Coronale - Moyenne: {correlations['coronal']['mean']:.3f}, Min: {correlations['coronal']['min']:.3f}")
    print(f"   Sagittale- Moyenne: {correlations['sagittal']['mean']:.3f}, Min: {correlations['sagittal']['min']:.3f}")
    
    alignment_info['correlations'] = correlations
    
    # 4. Détection de décalages
    print(f"\n4. DÉTECTION DE DÉCALAGES:")
    shifts = detect_volume_shifts(volume1, volume2)
    
    print(f"   Décalage estimé (X, Y, Z): ({shifts[0]:.1f}, {shifts[1]:.1f}, {shifts[2]:.1f}) voxels")
    
    alignment_info['estimated_shift'] = shifts
    
    # 5. Évaluation globale
    print(f"\n5. ÉVALUATION GLOBALE:")
    
    # Critères d'alignement
    correlation_threshold = 0.7
    shift_threshold = 2.0  # voxels
    com_threshold = 5.0    # voxels
    
    is_well_aligned = (
        correlations['axial']['mean'] > correlation_threshold and
        correlations['coronal']['mean'] > correlation_threshold and
        correlations['sagittal']['mean'] > correlation_threshold and
        np.max(np.abs(shifts)) < shift_threshold and
        com_distance < com_threshold
    )
    
    if is_well_aligned:
        print(f"   ✅ Les volumes semblent BIEN ALIGNÉS")
        print(f"   → Corrélations élevées (>{correlation_threshold})")
        print(f"   → Décalages faibles (<{shift_threshold} voxels)")
        print(f"   → Centres de masse proches (<{com_threshold} voxels)")
    else:
        print(f"   ❌ Les volumes semblent MAL ALIGNÉS")
        if np.any(np.array([correlations['axial']['mean'], correlations['coronal']['mean'], 
                           correlations['sagittal']['mean']]) < correlation_threshold):
            print(f"   → Corrélations faibles (<{correlation_threshold})")
        if np.max(np.abs(shifts)) >= shift_threshold:
            print(f"   → Décalages importants (≥{shift_threshold} voxels)")
        if com_distance >= com_threshold:
            print(f"   → Centres de masse éloignés (≥{com_threshold} voxels)")
    
    alignment_info['is_well_aligned'] = is_well_aligned
    alignment_info['recommendations'] = generate_alignment_recommendations(alignment_info)
    
    return alignment_info


def calculate_center_of_mass(volume):
    """
    Calcule le centre de masse d'un volume 3D.
    
    Args:
        volume (numpy.ndarray): Volume 3D
        
    Returns:
        tuple: Coordonnées (x, y, z) du centre de masse
    """
    # Utiliser les voxels non-zéro pour le calcul
    coords = np.where(volume > 0)
    if len(coords[0]) == 0:
        # Si aucun voxel non-zéro, retourner le centre géométrique
        return tuple(np.array(volume.shape) / 2)
    
    weights = volume[coords]
    com_x = np.average(coords[0], weights=weights)
    com_y = np.average(coords[1], weights=weights)
    com_z = np.average(coords[2], weights=weights)
    
    return (com_x, com_y, com_z)


def analyze_slice_correlations(volume1, volume2):
    """
    Analyse les corrélations entre les tranches correspondantes dans les 3 orientations.
    
    Args:
        volume1, volume2 (numpy.ndarray): Volumes à comparer
        
    Returns:
        dict: Corrélations pour chaque orientation
    """
    correlations = {
        'axial': {'correlations': [], 'mean': 0, 'min': 0},
        'coronal': {'correlations': [], 'mean': 0, 'min': 0},
        'sagittal': {'correlations': [], 'mean': 0, 'min': 0}
    }
    
    # Corrélations axiales (tranches Z)
    for z in range(volume1.shape[0]):
        slice1 = volume1[z, :, :]
        slice2 = volume2[z, :, :]
        if np.std(slice1) > 0 and np.std(slice2) > 0:
            corr = np.corrcoef(slice1.flatten(), slice2.flatten())[0, 1]
            if not np.isnan(corr):
                correlations['axial']['correlations'].append(corr)
    
    # Corrélations coronales (tranches Y)
    for y in range(volume1.shape[1]):
        slice1 = volume1[:, y, :]
        slice2 = volume2[:, y, :]
        if np.std(slice1) > 0 and np.std(slice2) > 0:
            corr = np.corrcoef(slice1.flatten(), slice2.flatten())[0, 1]
            if not np.isnan(corr):
                correlations['coronal']['correlations'].append(corr)
    
    # Corrélations sagittales (tranches X)
    for x in range(volume1.shape[2]):
        slice1 = volume1[:, :, x]
        slice2 = volume2[:, :, x]
        if np.std(slice1) > 0 and np.std(slice2) > 0:
            corr = np.corrcoef(slice1.flatten(), slice2.flatten())[0, 1]
            if not np.isnan(corr):
                correlations['sagittal']['correlations'].append(corr)
    
    # Calculer les statistiques
    for orientation in correlations:
        if correlations[orientation]['correlations']:
            correlations[orientation]['mean'] = np.mean(correlations[orientation]['correlations'])
            correlations[orientation]['min'] = np.min(correlations[orientation]['correlations'])
        else:
            correlations[orientation]['mean'] = 0
            correlations[orientation]['min'] = 0
    
    return correlations


def detect_volume_shifts(volume1, volume2, max_shift=10):
    """
    Détecte les décalages entre deux volumes en utilisant la corrélation croisée.
    
    Args:
        volume1, volume2 (numpy.ndarray): Volumes à comparer
        max_shift (int): Décalage maximum à tester en voxels
        
    Returns:
        tuple: Décalages estimés (dx, dy, dz)
    """
    # Utiliser une région d'intérêt centrale pour accélérer le calcul
    center = [s // 2 for s in volume1.shape]
    roi_size = min(64, min(volume1.shape) // 2)  # ROI de 64x64x64 maximum
    
    roi1 = volume1[
        center[0]-roi_size//2:center[0]+roi_size//2,
        center[1]-roi_size//2:center[1]+roi_size//2,
        center[2]-roi_size//2:center[2]+roi_size//2
    ]
    
    roi2 = volume2[
        center[0]-roi_size//2:center[0]+roi_size//2,
        center[1]-roi_size//2:center[1]+roi_size//2,
        center[2]-roi_size//2:center[2]+roi_size//2
    ]
    
    best_correlation = -1
    best_shift = (0, 0, 0)
    
    # Tester différents décalages
    for dx in range(-max_shift, max_shift + 1, 2):
        for dy in range(-max_shift, max_shift + 1, 2):
            for dz in range(-max_shift, max_shift + 1, 2):
                # Appliquer le décalage
                shifted_roi = np.roll(roi2, (dx, dy, dz), axis=(0, 1, 2))
                
                # Calculer la corrélation
                if np.std(roi1) > 0 and np.std(shifted_roi) > 0:
                    corr = np.corrcoef(roi1.flatten(), shifted_roi.flatten())[0, 1]
                    if not np.isnan(corr) and corr > best_correlation:
                        best_correlation = corr
                        best_shift = (dx, dy, dz)
    
    return best_shift


def generate_alignment_recommendations(alignment_info):
    """
    Génère des recommandations basées sur l'analyse d'alignement.
    
    Args:
        alignment_info (dict): Informations d'alignement
        
    Returns:
        list: Liste de recommandations
    """
    recommendations = []
    
    if not alignment_info.get('dimensions_match', True):
        recommendations.append("Effectuer un recalage spatial pour harmoniser les dimensions")
        recommendations.append("Vérifier les paramètres d'acquisition (résolution, FOV)")
    
    if alignment_info.get('center_of_mass', {}).get('distance', 0) > 5:
        recommendations.append("Considérer un recalage par translation basé sur les centres de masse")
    
    correlations = alignment_info.get('correlations', {})
    low_corr_orientations = []
    for orientation, data in correlations.items():
        if data.get('mean', 0) < 0.7:
            low_corr_orientations.append(orientation)
    
    if low_corr_orientations:
        recommendations.append(f"Corrélations faibles détectées dans les plans: {', '.join(low_corr_orientations)}")
        recommendations.append("Envisager un recalage rigide ou non-rigide")
    
    estimated_shift = alignment_info.get('estimated_shift', (0, 0, 0))
    if np.max(np.abs(estimated_shift)) > 2:
        recommendations.append(f"Décalage significatif détecté: {estimated_shift}")
        recommendations.append("Appliquer une correction de translation")
    
    if not recommendations:
        recommendations.append("✅ Les volumes semblent correctement alignés")
        recommendations.append("Aucune correction majeure nécessaire")
    
    return recommendations

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

