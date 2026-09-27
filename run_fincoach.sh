#!/bin/bash

# ==============================================================================
# Script de lancement automatique pour FinCoach IA
# ==============================================================================

# Se placer obligatoirement dans le répertoire du script
cd "$(dirname "$0")"

SCRIPT_DIR="$(pwd)"

# Exporter les PATHs usuels sur macOS (Homebrew, Local, etc.)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Détection et activation de l'environnement virtuel (.venv ou venv)
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "❌ Erreur : Aucun environnement virtuel trouvé dans $SCRIPT_DIR (.venv ou venv)"
    read -p "Appuyez sur n'importe quelle touche pour fermer..."
    exit 1
fi

# Vérification du fichier de données (génération automatique en secours)
if [ ! -f "$SCRIPT_DIR/transactions.csv" ]; then
    echo "📊 Génération du jeu de données initial..."
    python generate_data.py
fi

# Lancement de l'application Streamlit dans la console
echo "🚀 Lancement de FinCoach IA..."
streamlit run "$SCRIPT_DIR/app.py"
