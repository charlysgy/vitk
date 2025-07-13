#!/bin/bash

# Définir les couleurs
RESET="\033[0m"
WHITE="\033[1;37m"
GREEN="\033[1;32m"
RED="\033[1;31m"

# Message info
function info() {
    echo -e "${WHITE}$1${RESET}"
}

# Message succès
function success() {
    echo -e "${GREEN}$1${RESET}"
}

# Message erreur
function error() {
    echo -e "${RED}$1${RESET}"
}

info "🔍 Activation de l'environnement virtuel..."

# Vérifie que .venv existe
if [ ! -d ".venv" ]; then
    error "❌ Environnement virtuel '.venv' non trouvé !"
    info "Création de l'environnement virtuel..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        error "❌ Échec de la création de l'environnement virtuel."
        exit 1
    else
        success "✅ Environnement virtuel créé avec succès."
    fi
fi

# Active l'environnement virtuel selon le système
if [ -f ".venv/bin/activate" ]; then
    . .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    . .venv/Scripts/activate
else
    error "❌ Fichier d'activation introuvable dans '.venv'."
    exit 1
fi

success "✅ Environnement activé."

# Vérifie les dépendances
info "📦 Vérification des dépendances..."

missing=false

for package in vtk itk; do
    python3 -c "import $package" 2>/dev/null
    if [ $? -ne 0 ]; then
        error "❌ Dépendance manquante : $package"
        missing=true
    else
        success "✔️  $package est installé."
    fi
done

if [ "$missing" = true ]; then
    error "🚫 Une ou plusieurs dépendances sont manquantes."
    info "Installation des dépendances..."
    pip install vtk itk
    if [ $? -ne 0 ]; then
        error "❌ Échec de l'installation des dépendances."
    else
        success "✅ Dépendances installées avec succès."
    fi
else
    success "✅ Toutes les dépendances sont présentes."
fi

# Vérifie la présence de main.py
if [ ! -f "main.py" ]; then
    error "❌ Fichier 'main.py' introuvable."
    exit 1
fi

# Lance le script
info "🚀 Lancement de l'application Python..."
python3 main.py

# Affiche un message si le script s'est terminé correctement
if [ $? -eq 0 ]; then
    success "✅ Exécution terminée avec succès."
else
    error "❌ Erreur pendant l'exécution de main.py."
fi
