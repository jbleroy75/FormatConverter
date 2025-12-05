#!/bin/bash

# Script d'installation des outils de conversion
# Format Converter - macOS

echo "🔧 Installation des outils de conversion pour Format Converter"
echo "=============================================================="
echo ""

# Ajouter Homebrew au PATH (Apple Silicon et Intel)
if [ -f "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Vérifier si Homebrew est installé
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew n'est pas installé."
    echo "   Installez-le d'abord : https://brew.sh"
    echo ""
    echo "   Commande d'installation :"
    echo '   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo "✅ Homebrew détecté"
echo ""

# Liste des outils à installer
echo "📦 Outils à installer :"
echo "   - ffmpeg (audio/vidéo)"
echo "   - pandoc (documents)"
echo "   - p7zip (archives 7z)"
echo "   - unrar (archives RAR)"
echo "   - webp (images WebP)"
echo ""

read -p "Voulez-vous installer tous ces outils ? (o/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Oo]$ ]]; then
    echo ""
    echo "🔄 Installation en cours..."
    echo ""
    
    # FFmpeg
    echo "📹 Installation de FFmpeg..."
    brew install ffmpeg
    
    # Pandoc
    echo "📄 Installation de Pandoc..."
    brew install pandoc
    
    # p7zip
    echo "📦 Installation de p7zip..."
    brew install p7zip
    
    # unrar
    echo "📦 Installation de unrar..."
    brew install unrar
    
    # webp
    echo "🖼️ Installation de WebP..."
    brew install webp
    
    echo ""
    echo "✅ Installation terminée !"
    echo ""
    
    # Vérification
    echo "📋 Vérification des outils :"
    echo ""
    
    check_tool() {
        if command -v $1 &> /dev/null || [ -f "/opt/homebrew/bin/$1" ] || [ -f "/usr/local/bin/$1" ]; then
            echo "   ✅ $2"
        else
            echo "   ❌ $2"
        fi
    }
    
    check_tool "ffmpeg" "FFmpeg"
    check_tool "pandoc" "Pandoc"
    check_tool "7z" "7-Zip"
    check_tool "unrar" "Unrar"
    check_tool "cwebp" "WebP"
    
    echo ""
    
    # LibreOffice (optionnel)
    read -p "Voulez-vous aussi installer LibreOffice (pour Word/Excel) ? (o/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo "📝 Installation de LibreOffice..."
        brew install --cask libreoffice
        echo "✅ LibreOffice installé !"
    fi
    
else
    echo "Installation annulée."
fi

echo ""
echo "🚀 Vous pouvez maintenant ouvrir FormatConverter.xcodeproj avec Xcode !"
