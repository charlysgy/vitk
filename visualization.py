"""
Visualization Module
===================

Ce module contient les classes et fonctions pour la visualisation interactive
des volumes médicaux en utilisant VTK.

Classes:
    - InteractiveImageViewer: Visualiseur interactif pour la comparaison de volumes

Fonctions:
    - show_interactive_comparison: Fonction de convenance pour l'affichage
"""

import vtk
import numpy as np

# Gestion des imports relatifs/absolus pour compatibilité
try:
    from .converters import simple_numpy_to_vtk
    from .utils import calculate_intensity_stats, print_intensity_stats
except ImportError:
    # Fallback pour exécution directe
    from converters import simple_numpy_to_vtk
    from utils import calculate_intensity_stats, print_intensity_stats


class InteractiveImageViewer:
    """
    Visualiseur interactif pour la comparaison de deux volumes médicaux.
    
    Permet la navigation dans les trois orientations (axiale, coronale, sagittale)
    avec affichage côte-à-côte des deux volumes.
    """
    
    def __init__(self, volume1, volume2):
        """
        Initialise le visualiseur avec deux volumes.
        
        Args:
            volume1, volume2 (numpy.ndarray): Volumes 3D à comparer
        """
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
        stats = calculate_intensity_stats(self.volume1, self.volume2)
        
        if 'display' in stats:
            self.window = stats['display']['window']
            self.level = stats['display']['level']
            self.min_intensity = stats['combined']['min_intensity']
            self.max_intensity = stats['combined']['max_intensity']
        else:
            # Fallback si un seul volume
            self.min_intensity = stats['volume1']['percentile_1']
            self.max_intensity = stats['volume1']['percentile_99']
            self.window = self.max_intensity - self.min_intensity
            self.level = (self.max_intensity + self.min_intensity) / 2
        
        print(f"Niveaux d'intensité calculés:")
        print(f"  Min: {self.min_intensity:.2f}, Max: {self.max_intensity:.2f}")
        print(f"  Window: {self.window:.2f}, Level: {self.level:.2f}")
    
    def setup_gui(self):
        """Configure l'interface graphique VTK"""
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
        
        # Style d'interaction personnalisé
        style = vtk.vtkInteractorStyleImage()
        self.interactor.SetInteractorStyle(style)
    
    def setup_pipeline(self):
        """Configure le pipeline de rendu VTK"""
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
        elif key == 'a':
            # Vérification d'alignement à la position actuelle
            self.check_alignment_interactively()
        elif key == 'd':
            # Toggle mode différence
            self.toggle_difference_mode()
        elif key == 's':
            # Sauvegarder rapport d'alignement
            self.save_alignment_report()
        else:
            return
        
        if key not in ['q', 'Escape', 'a', 'd', 's']:
            self.update_slices()
            self.print_current_position()
    
    def print_current_position(self):
        """Affiche la position actuelle des coupes"""
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
    
    def print_controls(self):
        """Affiche les contrôles disponibles"""
        print("\n=== CONTRÔLES ===")
        print("NAVIGATION:")
        print("  ↑/↓ : Navigation axiale")
        print("  ←/→ : Navigation sagittale") 
        print("  Page Up/Down : Navigation coronale")
        print("\nVÉRIFICATION D'ALIGNEMENT:")
        print("  'a' : Analyser l'alignement à la position actuelle")
        print("  'd' : Activer/désactiver le mode différence")
        print("  's' : Sauvegarder rapport d'alignement")
        print("\nAUTRES:")
        print("  'q' ou 'Escape' : Quitter")
        print("  Fermeture fenêtre : Alt+F4 ou bouton X")
    
    def show(self):
        """Affiche la vue interactive"""
        self.print_controls()
        
        try:
            self.render_window.Render()
            self.interactor.Start()
        except KeyboardInterrupt:
            print("\nInterruption clavier détectée...")
            self.cleanup_and_exit()
        except Exception as e:
            print(f"Erreur lors de l'affichage: {e}")
            self.cleanup_and_exit()
    
    def check_alignment_interactively(self):
        """Affiche des informations d'alignement pour la position actuelle"""
        print(f"\n=== VÉRIFICATION D'ALIGNEMENT À LA POSITION ACTUELLE ===")
        print(f"Position: Axial={self.axial_slice}, Coronal={self.coronal_slice}, Sagittal={self.sagittal_slice}")
        
        # Extraire les tranches actuelles
        axial1 = self.volume1[self.axial_slice, :, :]
        axial2 = self.volume2[self.axial_slice, :, :]
        
        coronal1 = self.volume1[:, self.coronal_slice, :]
        coronal2 = self.volume2[:, self.coronal_slice, :]
        
        sagittal1 = self.volume1[:, :, self.sagittal_slice]
        sagittal2 = self.volume2[:, :, self.sagittal_slice]
        
        # Calculer les corrélations
        def safe_correlation(slice1, slice2):
            if np.std(slice1) > 0 and np.std(slice2) > 0:
                corr = np.corrcoef(slice1.flatten(), slice2.flatten())[0, 1]
                return corr if not np.isnan(corr) else 0.0
            return 0.0
        
        corr_axial = safe_correlation(axial1, axial2)
        corr_coronal = safe_correlation(coronal1, coronal2)
        corr_sagittal = safe_correlation(sagittal1, sagittal2)
        
        print(f"Corrélations:")
        print(f"  Axiale  : {corr_axial:.3f} {'✅' if corr_axial > 0.7 else '❌' if corr_axial < 0.5 else '⚠️'}")
        print(f"  Coronale: {corr_coronal:.3f} {'✅' if corr_coronal > 0.7 else '❌' if corr_coronal < 0.5 else '⚠️'}")
        print(f"  Sagittale: {corr_sagittal:.3f} {'✅' if corr_sagittal > 0.7 else '❌' if corr_sagittal < 0.5 else '⚠️'}")
        
        # Moyennes d'intensité pour détecter des différences importantes
        print(f"Intensités moyennes:")
        print(f"  Vol1 - Axiale: {axial1.mean():.1f}, Coronale: {coronal1.mean():.1f}, Sagittale: {sagittal1.mean():.1f}")
        print(f"  Vol2 - Axiale: {axial2.mean():.1f}, Coronale: {coronal2.mean():.1f}, Sagittale: {sagittal2.mean():.1f}")
    
    def toggle_difference_mode(self):
        """Active/désactive l'affichage des différences"""
        if not hasattr(self, 'difference_mode'):
            self.difference_mode = False
        
        self.difference_mode = not self.difference_mode
        
        if self.difference_mode:
            print("Mode différence ACTIVÉ - Affichage des différences entre volumes")
            self.setup_difference_pipeline()
        else:
            print("Mode différence DÉSACTIVÉ - Retour à l'affichage normal")
            self.restore_normal_pipeline()
        
        self.update_slices()
    
    def setup_difference_pipeline(self):
        """Configure le pipeline pour afficher les différences"""
        # Calculer le volume de différence seulement si ce n'est pas déjà fait
        if not hasattr(self, 'vtk_diff'):
            diff_volume = np.abs(self.volume2 - self.volume1)
            self.vtk_diff = simple_numpy_to_vtk(diff_volume)
        
        # Reconfigurer les pipelines pour afficher les différences
        orientations = ['axial', 'coronal', 'sagittal']
        
        for vol_idx in range(2):
            for orient_idx, orientation in enumerate(orientations):
                reslice_idx = vol_idx * 3 + orient_idx
                reslice = self.reslice_cursors[reslice_idx]
                
                if vol_idx == 0:
                    # Volume 1 normal
                    reslice.SetInputData(self.vtk_volume1)
                else:
                    # Volume 2 remplacé par les différences
                    reslice.SetInputData(self.vtk_diff)
                
                reslice.Update()
    
    def restore_normal_pipeline(self):
        """Restaure le pipeline normal (sans différences)"""
        orientations = ['axial', 'coronal', 'sagittal']
        volumes = [self.vtk_volume1, self.vtk_volume2]
        
        for vol_idx, volume in enumerate(volumes):
            for orient_idx, orientation in enumerate(orientations):
                reslice_idx = vol_idx * 3 + orient_idx
                reslice = self.reslice_cursors[reslice_idx]
                
                # Restaurer le volume original
                reslice.SetInputData(volume)
                reslice.Update()
    
    def save_alignment_report(self):
        """Sauvegarde un rapport d'alignement dans un fichier"""
        try:
            # Import local pour éviter les problèmes de dépendances circulaires
            try:
                from .utils import check_volume_alignment
            except ImportError:
                from utils import check_volume_alignment
            
            alignment_info = check_volume_alignment(self.volume1, self.volume2)
            
            with open("alignment_report.txt", "w", encoding="utf-8") as f:
                f.write("RAPPORT D'ALIGNEMENT SPATIAL\n")
                f.write("="*50 + "\n\n")
                f.write(f"Dimensions: {self.volume1.shape}\n")
                f.write(f"Alignement correct: {'✅ OUI' if alignment_info.get('is_well_aligned', False) else '❌ NON'}\n\n")
                
                f.write("RECOMMANDATIONS:\n")
                for i, rec in enumerate(alignment_info.get('recommendations', []), 1):
                    f.write(f"{i}. {rec}\n")
            
            print("✅ Rapport d'alignement sauvegardé dans 'alignment_report.txt'")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            

def show_interactive_comparison(volume1, volume2):
    """
    Fonction de convenance pour afficher la comparaison interactive de deux volumes.
    
    Args:
        volume1, volume2 (numpy.ndarray): Volumes 3D à comparer
    """
    viewer = InteractiveImageViewer(volume1, volume2)
    viewer.show()
