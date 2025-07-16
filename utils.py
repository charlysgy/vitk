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

import numpy as np


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
