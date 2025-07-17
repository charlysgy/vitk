"""
Converters Module
================

Ce module contient toutes les fonctions de conversion entre les différents
formats d'images : ITK, NumPy et VTK.

Fonctions:
    - itk_to_numpy: Conversion d'une image ITK vers un array NumPy
    - numpy_to_vtk_volume: Conversion d'un array NumPy vers VTK avec transposition
    - simple_numpy_to_vtk: Conversion simplifiée NumPy vers VTK
"""

import itk
import vtk
from vtk.util import numpy_support
import numpy as np


def itk_to_numpy(image_itk):
    """
    Convertit une image ITK en array NumPy.
    
    Args:
        image_itk: Image au format ITK
        
    Returns:
        numpy.ndarray: Array NumPy correspondant
    """
    return itk.GetArrayFromImage(image_itk)


def numpy_to_vtk_volume(numpy_array):
    """
    Convertit un volume numpy 3D en vtkImageData avec transposition.
    
    ITK utilise l'ordre ZYX, on transpose pour avoir XYZ pour VTK.
    
    Args:
        numpy_array (numpy.ndarray): Array 3D à convertir
        
    Returns:
        vtk.vtkImageData: Volume VTK résultant
    """
    # ITK utilise l'ordre ZYX, on transpose pour avoir XYZ pour VTK
    vtk_array = numpy_array.transpose(2, 1, 0)
    flat_array = vtk_array.flatten()
    vtk_data_array = numpy_support.numpy_to_vtk(
        num_array=flat_array, 
        deep=True, 
        array_type=vtk.VTK_FLOAT
    )
    
    image = vtk.vtkImageData()
    image.SetDimensions(vtk_array.shape[0], vtk_array.shape[1], vtk_array.shape[2])
    image.SetSpacing(1.0, 1.0, 1.0)
    image.SetOrigin(0.0, 0.0, 0.0)
    image.GetPointData().SetScalars(vtk_data_array)
    return image


def simple_numpy_to_vtk(numpy_array):
    """
    Version simplifiée de la conversion numpy vers VTK.
    
    Pas de transposition - utilise l'ordre ITK direct.
    
    Args:
        numpy_array (numpy.ndarray): Array 3D à convertir
        
    Returns:
        vtk.vtkImageData: Volume VTK résultant
    """
    flat_array = numpy_array.flatten()
    vtk_data_array = numpy_support.numpy_to_vtk(
        num_array=flat_array, 
        deep=True, 
        array_type=vtk.VTK_FLOAT
    )
    
    image = vtk.vtkImageData()
    # Utiliser les dimensions dans l'ordre ITK (Z,Y,X)
    image.SetDimensions(numpy_array.shape[2], numpy_array.shape[1], numpy_array.shape[0])
    image.SetSpacing(1.0, 1.0, 1.0)
    image.SetOrigin(0.0, 0.0, 0.0)
    image.GetPointData().SetScalars(vtk_data_array)
    return image


def load_medical_image(file_path, pixel_type=itk.F):
    """
    Charge une image médicale avec ITK.
    
    Args:
        file_path (str): Chemin vers le fichier image
        pixel_type: Type de pixel ITK (par défaut itk.F pour float)
        
    Returns:
        tuple: (image_itk, numpy_array) - Image ITK et array NumPy correspondant
    """
    try:
        image_itk = itk.imread(file_path, pixel_type)
        numpy_array = itk_to_numpy(image_itk)
        return image_itk, numpy_array
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement de {file_path}: {e}")
