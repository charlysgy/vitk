import itk
import vtk
from vtk.util import numpy_support
import numpy as np

def itk_to_numpy(image_itk):
    return itk.GetArrayFromImage(image_itk)

def numpy_to_vtk_volume(numpy_array):
    """Convertit un volume numpy 3D en vtkImageData"""
    # ITK utilise l'ordre ZYX, on transpose pour avoir XYZ pour VTK
    vtk_array = numpy_array.transpose(2, 1, 0)
    flat_array = vtk_array.flatten()
    vtk_data_array = numpy_support.numpy_to_vtk(num_array=flat_array, deep=True, array_type=vtk.VTK_FLOAT)
    
    image = vtk.vtkImageData()
    image.SetDimensions(vtk_array.shape[0], vtk_array.shape[1], vtk_array.shape[2])
    image.SetSpacing(1.0, 1.0, 1.0)
    image.SetOrigin(0.0, 0.0, 0.0)
    image.GetPointData().SetScalars(vtk_data_array)
    return image

# Fonctions de diagnostic et de test
def debug_array_info(array, name):
    """Affiche des informations de débogage sur un array"""
    print(f"\n=== {name} ===")
    print(f"Shape: {array.shape}")
    print(f"Dtype: {array.dtype}")
    print(f"Min: {array.min():.2f}, Max: {array.max():.2f}")
    print(f"Mean: {array.mean():.2f}, Std: {array.std():.2f}")
    print(f"Non-zero count: {np.count_nonzero(array)}/{array.size}")

def simple_numpy_to_vtk(numpy_array):
    """Version simplifiée de la conversion numpy vers VTK"""
    # Pas de transposition pour commencer - utiliser l'ordre ITK direct
    flat_array = numpy_array.flatten()
    vtk_data_array = numpy_support.numpy_to_vtk(num_array=flat_array, deep=True, array_type=vtk.VTK_FLOAT)
    
    image = vtk.vtkImageData()
    # Utiliser les dimensions dans l'ordre ITK (Z,Y,X)
    image.SetDimensions(numpy_array.shape[2], numpy_array.shape[1], numpy_array.shape[0])
    image.SetSpacing(1.0, 1.0, 1.0)
    image.SetOrigin(0.0, 0.0, 0.0)
    image.GetPointData().SetScalars(vtk_data_array)
    return image

class InteractiveImageViewer:
    def __init__(self, volume1, volume2):
        self.volume1 = volume1
        self.volume2 = volume2
        self.shape = volume1.shape
        
        # Calculer les niveaux d'intensité automatiquement
        self.calculate_intensity_levels()
        
        # Position actuelle des coupes
        self.axial_slice = self.shape[0] // 2
        self.coronal_slice = self.shape[1] // 2
        self.sagittal_slice = self.shape[2] // 2
        
        # Conversion en VTK - utiliser la version simplifiée pour débugger
        self.vtk_volume1 = simple_numpy_to_vtk(volume1)
        self.vtk_volume2 = simple_numpy_to_vtk(volume2)
        
        # Initialisation des composants VTK
        self.reslice_cursors = []
        self.image_actors = []
        self.renderers = []
        
        self.setup_gui()
        self.setup_pipeline()
    
    def calculate_intensity_levels(self):
        """Calcule automatiquement les niveaux d'intensité optimaux"""
        # Combiner les deux volumes pour calculer les niveaux globaux
        combined = np.concatenate([self.volume1.flatten(), self.volume2.flatten()])
        
        # Exclure les valeurs nulles et aberrantes
        non_zero = combined[combined > 0]
        if len(non_zero) > 0:
            self.min_intensity = np.percentile(non_zero, 1)
            self.max_intensity = np.percentile(non_zero, 99)
            self.window = self.max_intensity - self.min_intensity
            self.level = (self.max_intensity + self.min_intensity) / 2
        else:
            self.min_intensity = combined.min()
            self.max_intensity = combined.max()
            self.window = self.max_intensity - self.min_intensity
            self.level = (self.max_intensity + self.min_intensity) / 2
        
        print(f"Niveaux d'intensité calculés:")
        print(f"  Min: {self.min_intensity:.2f}, Max: {self.max_intensity:.2f}")
        print(f"  Window: {self.window:.2f}, Level: {self.level:.2f}")
    
    def setup_pipeline(self):
        # Configuration pour les 6 vues (3 orientations x 2 volumes)
        orientations = ['axial', 'coronal', 'sagittal']
        volumes = [self.vtk_volume1, self.vtk_volume2]
        
        for vol_idx, volume in enumerate(volumes):
            for orient_idx, orientation in enumerate(orientations):
                # Reslice pour extraire la coupe
                reslice = vtk.vtkImageReslice()
                reslice.SetInputData(volume)
                reslice.SetInterpolationModeToLinear()
                reslice.SetOutputDimensionality(2)
                
                # Configuration de l'orientation
                if orientation == 'axial':
                    reslice.SetResliceAxesDirectionCosines(1,0,0, 0,1,0, 0,0,1)
                elif orientation == 'coronal':
                    reslice.SetResliceAxesDirectionCosines(1,0,0, 0,0,-1, 0,1,0)
                else:  # sagittal
                    reslice.SetResliceAxesDirectionCosines(0,1,0, 0,0,-1, 1,0,0)
                
                # Mapper pour convertir l'image en rendu 2D
                mapper = vtk.vtkImageSliceMapper()
                mapper.SetInputConnection(reslice.GetOutputPort())
                
                # Actor pour afficher l'image
                actor = vtk.vtkImageSlice()
                actor.SetMapper(mapper)
                
                # Configuration des propriétés d'affichage
                property = actor.GetProperty()
                property.SetColorWindow(self.window)
                property.SetColorLevel(self.level)
                property.SetInterpolationTypeToLinear()
                
                # Ajouter à la liste
                self.reslice_cursors.append(reslice)
                self.image_actors.append(actor)
                
                # Ajouter l'actor au renderer correspondant
                renderer_idx = vol_idx * 3 + orient_idx
                self.renderers[renderer_idx].AddViewProp(actor)
        
        self.update_slices()
    
    def setup_gui(self):
        # Fenêtre principale
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1800, 900)
        self.render_window.SetWindowName("Navigation Interactive - Avant/Après")
        
        # Interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.render_window.SetInteractor(self.interactor)
        
        # Configuration des viewports (2x3 grid)
        viewports = [
            [0.0, 0.5, 0.33, 1.0],   # Volume1 - Axial
            [0.33, 0.5, 0.66, 1.0],  # Volume1 - Coronal  
            [0.66, 0.5, 1.0, 1.0],   # Volume1 - Sagittal
            [0.0, 0.0, 0.33, 0.5],   # Volume2 - Axial
            [0.33, 0.0, 0.66, 0.5],  # Volume2 - Coronal
            [0.66, 0.0, 1.0, 0.5],   # Volume2 - Sagittal
        ]
        
        titles = [
            "Volume 1 - Axial", "Volume 1 - Coronal", "Volume 1 - Sagittal",
            "Volume 2 - Axial", "Volume 2 - Coronal", "Volume 2 - Sagittal"
        ]
        
        # Créer les renderers
        for i, (viewport, title) in enumerate(zip(viewports, titles)):
            renderer = vtk.vtkRenderer()
            renderer.SetViewport(*viewport)
            renderer.SetBackground(0.1, 0.1, 0.1)
            
            # Ajouter un titre
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(title)
            text_actor.GetTextProperty().SetFontSize(14)
            text_actor.GetTextProperty().SetColor(1, 1, 1)
            text_actor.SetPosition(10, 10)
            renderer.AddActor(text_actor)
            
            self.renderers.append(renderer)
            self.render_window.AddRenderer(renderer)
        
        # Réinitialiser les caméras après avoir ajouté tous les renderers
        for renderer in self.renderers:
            renderer.ResetCamera()
        
        # Gestionnaire d'événements clavier et fermeture
        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)
        self.interactor.AddObserver("ExitEvent", self.on_exit)
        
        # Style d'interaction personnalisé pour i3wm
        style = vtk.vtkInteractorStyleImage()
        self.interactor.SetInteractorStyle(style)
    
    def update_slices(self):
        """Met à jour la position des coupes pour toutes les vues"""
        orientations = ['axial', 'coronal', 'sagittal']
        slices = [self.axial_slice, self.coronal_slice, self.sagittal_slice]
        
        for vol_idx in range(2):  # 2 volumes
            for orient_idx, (orientation, slice_pos) in enumerate(zip(orientations, slices)):
                reslice_idx = vol_idx * 3 + orient_idx
                reslice = self.reslice_cursors[reslice_idx]
                
                # Position de la coupe selon l'orientation
                if orientation == 'axial':
                    reslice.SetResliceAxesOrigin(0, 0, slice_pos)
                elif orientation == 'coronal':
                    reslice.SetResliceAxesOrigin(0, slice_pos, 0)
                else:  # sagittal
                    reslice.SetResliceAxesOrigin(slice_pos, 0, 0)
                
                reslice.Update()
                
                # Réinitialiser la caméra pour chaque renderer
                renderer = self.renderers[reslice_idx]
                renderer.ResetCamera()
        
        if hasattr(self, 'render_window'):
            self.render_window.Render()
    
    def on_key_press(self, obj, event):
        """Gestionnaire des événements clavier pour la navigation"""
        key = self.interactor.GetKeySym()
        
        if key == 'q' or key == 'Escape':
            print("Fermeture de l'application...")
            self.cleanup_and_exit()
        elif key == 'Up':
            self.axial_slice = min(self.axial_slice + 1, self.shape[0] - 1)
        elif key == 'Down':
            self.axial_slice = max(self.axial_slice - 1, 0)
        elif key == 'Left':
            self.sagittal_slice = max(self.sagittal_slice - 1, 0)
        elif key == 'Right':
            self.sagittal_slice = min(self.sagittal_slice + 1, self.shape[2] - 1)
        elif key == 'Prior':  # Page Up
            self.coronal_slice = min(self.coronal_slice + 1, self.shape[1] - 1)
        elif key == 'Next':   # Page Down
            self.coronal_slice = max(self.coronal_slice - 1, 0)
        else:
            return
        
        if key not in ['q', 'Escape']:
            self.update_slices()
            print(f"Position: Axial={self.axial_slice}/{self.shape[0]-1}, "
                  f"Coronal={self.coronal_slice}/{self.shape[1]-1}, "
                  f"Sagittal={self.sagittal_slice}/{self.shape[2]-1}")
    
    def on_exit(self, obj, event):
        """Gestionnaire pour la fermeture de fenêtre"""
        print("Événement de fermeture détecté...")
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Nettoie les ressources et ferme proprement l'application"""
        try:
            # Arrêter l'interactor
            if hasattr(self, 'interactor') and self.interactor:
                self.interactor.ExitCallback()
                self.interactor.TerminateApp()
            
            # Fermer la fenêtre de rendu
            if hasattr(self, 'render_window') and self.render_window:
                self.render_window.Finalize()
                
            # Nettoyer les références
            self.render_window = None
            self.interactor = None
            
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
        finally:
            import sys
            sys.exit(0)
    
    def show(self):
        """Affiche la vue interactive"""
        print("Contrôles:")
        print("  ↑/↓ : Navigation axiale")
        print("  ←/→ : Navigation sagittale") 
        print("  Page Up/Down : Navigation coronale")
        print("  'q' ou 'Escape' : Quitter")
        print("  Fermeture fenêtre : Alt+F4 ou bouton X")
        
        try:
            self.render_window.Render()
            self.interactor.Start()
        except KeyboardInterrupt:
            print("\nInterruption clavier détectée...")
            self.cleanup_and_exit()
        except Exception as e:
            print(f"Erreur lors de l'affichage: {e}")
            self.cleanup_and_exit()

def show_interactive_comparison(volume1, volume2):
    """Fonction principale pour afficher la comparaison interactive"""
    viewer = InteractiveImageViewer(volume1, volume2)
    viewer.show()


# Chargement des volumes avec ITK
image1 = itk.imread("./Data/case6_gre1.nrrd", itk.F)
image2 = itk.imread("./Data/case6_gre2.nrrd", itk.F)

# Conversion ITK → NumPy
array1 = itk_to_numpy(image1)
array2 = itk_to_numpy(image2)

# Debug des données
debug_array_info(array1, "Array1")
debug_array_info(array2, "Array2")

# Test avec une coupe simple pour vérifier
print(f"\nTest coupe centrale:")
mid_slice = array1[array1.shape[0]//2, :, :]
print(f"Coupe centrale shape: {mid_slice.shape}")
print(f"Coupe centrale min/max: {mid_slice.min():.2f}/{mid_slice.max():.2f}")

# Affichage interactif avant/après avec navigation
show_interactive_comparison(array1, array2)

debug_array_info(array1, "Array 1")
debug_array_info(array2, "Array 2")

# Test de la conversion simplifiée
vtk_image1_simple = simple_numpy_to_vtk(array1)
vtk_image2_simple = simple_numpy_to_vtk(array2)