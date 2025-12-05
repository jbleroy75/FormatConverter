# 🔄 Format Converter

<p align="center">
  <img src="https://img.shields.io/badge/macOS-13.0+-blue.svg" alt="macOS">
  <img src="https://img.shields.io/badge/Swift-5.9-orange.svg" alt="Swift">
  <img src="https://img.shields.io/badge/SwiftUI-Native-green.svg" alt="SwiftUI">
  <img src="https://img.shields.io/badge/Python-3.9+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
</p>

<p align="center">
  <b>Application macOS native pour convertir tous types de fichiers en quelques clics.</b><br>
  Documents • Images • Audio • Vidéo • Archives • Données
</p>

---

## ✨ Fonctionnalités

### 📄 Documents
| Format | Extension | Conversion |
|--------|-----------|------------|
| PDF | `.pdf` | ✅ Lecture & Écriture |
| Word | `.docx` `.doc` | ✅ Via LibreOffice |
| Texte | `.txt` | ✅ Natif |
| Rich Text | `.rtf` | ✅ Natif |
| HTML | `.html` | ✅ Natif |
| Markdown | `.md` | ✅ Natif |
| EPUB | `.epub` | ✅ Via Pandoc |

### 🖼️ Images
| Format | Extension | Conversion |
|--------|-----------|------------|
| PNG | `.png` | ✅ Natif |
| JPEG | `.jpg` `.jpeg` | ✅ Natif |
| HEIC | `.heic` | ✅ Natif (macOS) |
| WebP | `.webp` | ✅ Via cwebp |
| GIF | `.gif` | ✅ Natif |
| TIFF | `.tiff` | ✅ Natif |
| BMP | `.bmp` | ✅ Natif |

### 🎵 Audio
| Format | Extension | Conversion |
|--------|-----------|------------|
| MP3 | `.mp3` | ✅ Via FFmpeg |
| WAV | `.wav` | ✅ Via FFmpeg |
| AAC | `.aac` | ✅ Via FFmpeg |
| FLAC | `.flac` | ✅ Via FFmpeg |
| M4A | `.m4a` | ✅ Via FFmpeg |
| OGG | `.ogg` | ✅ Via FFmpeg |

### 🎬 Vidéo
| Format | Extension | Conversion |
|--------|-----------|------------|
| MP4 | `.mp4` | ✅ Via FFmpeg |
| MOV | `.mov` | ✅ Via FFmpeg |
| AVI | `.avi` | ✅ Via FFmpeg |
| MKV | `.mkv` | ✅ Via FFmpeg |
| WebM | `.webm` | ✅ Via FFmpeg |

### 📦 Archives
| Format | Extension | Conversion |
|--------|-----------|------------|
| ZIP | `.zip` | ✅ Natif |
| TAR | `.tar` | ✅ Natif |
| GZIP | `.gz` | ✅ Natif |
| 7-Zip | `.7z` | ✅ Via p7zip |
| RAR | `.rar` | ✅ Via unar |

### 📊 Données
| Format | Extension | Conversion |
|--------|-----------|------------|
| JSON | `.json` | ✅ Natif |
| CSV | `.csv` | ✅ Natif |
| XML | `.xml` | ✅ Natif |
| YAML | `.yaml` | ✅ Natif |
| PLIST | `.plist` | ✅ Natif |

---

## 📸 Captures d'écran

### Application Python (disponible maintenant)

```
┌────────────────────────────────────────────────────────────────┐
│                     🔄 Format Converter                         │
├─────────────────┬──────────────────────────────────────────────┤
│  FORMAT         │                                              │
│                 │            📁                                │
│  📄 DOCUMENTS   │                                              │
│   ● PDF         │     Déposez vos fichiers ici                │
│   ○ Word        │     ou cliquez pour parcourir               │
│   ○ Texte       │                                              │
│                 │         [ Parcourir ]                        │
│  🖼️ IMAGES      │                                              │
│   ○ PNG         ├──────────────────────────────────────────────┤
│   ○ JPEG        │  Fichiers sélectionnés           0 fichier  │
│   ○ HEIC        │  ┌────────────────────────────────────────┐ │
│   ○ WebP        │  │                                        │ │
│                 │  │   Aucun fichier sélectionné            │ │
│  🎵 AUDIO       │  │                                        │ │
│   ○ MP3         │  └────────────────────────────────────────┘ │
│   ○ WAV         │                                              │
│                 │  ┌────────────────────────────────────────┐ │
│  🎬 VIDÉO       │  │            Convertir                    │ │
│   ○ MP4         │  └────────────────────────────────────────┘ │
│   ○ MOV         │                                              │
│                 │  📂 Dossier de sortie: Downloads   [Changer] │
│  📦 ARCHIVES    │                                              │
│   ○ ZIP         │                                              │
└─────────────────┴──────────────────────────────────────────────┘
```

### Design moderne style macOS Sonoma
- 🎨 Interface sombre élégante
- 📁 Sidebar avec catégories
- 🖱️ Drag & Drop intuitif
- ✨ Animations fluides
- 🌙 Mode sombre natif

---

## 🚀 Installation

### Prérequis
- macOS 13.0 (Ventura) ou supérieur
- Python 3.9+ (pour la version Python)
- Xcode 15+ (pour la version Swift)

### Option 1 : Version Python (recommandée pour commencer)

```bash
# Cloner le repository
git clone https://github.com/jbleroy75/FormatConverter.git
cd FormatConverter

# Installer les dépendances Python
pip3 install customtkinter Pillow

# Lancer l'application
python3 FormatConverterApp.py
```

### Option 2 : Version Swift/Xcode

```bash
# Ouvrir le projet Xcode
open FormatConverter.xcodeproj

# Puis dans Xcode :
# 1. Sélectionner votre équipe de développement (Signing)
# 2. Appuyer sur ⌘ + R pour lancer
```

---

## 🛠️ Outils de conversion

Installez ces outils via [Homebrew](https://brew.sh) pour bénéficier de toutes les conversions :

```bash
# Installer Homebrew (si pas déjà fait)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer tous les outils
brew install ffmpeg      # Audio/Vidéo
brew install pandoc      # Documents
brew install p7zip       # Archives 7z
brew install unar        # Archives RAR
brew install webp        # Images WebP

# Optionnel : LibreOffice pour Word/Excel
brew install --cask libreoffice
```

Ou utilisez le script d'installation inclus :

```bash
./install-tools.sh
```

---

## 📁 Structure du projet

```
FormatConverter/
├── 📄 FormatConverterApp.py      # App Python (CustomTkinter)
├── 📄 install-tools.sh           # Script d'installation
├── 📄 README.md
│
├── 📁 FormatConverter/           # App Swift/SwiftUI
│   ├── FormatConverterApp.swift
│   ├── ContentView.swift
│   ├── Models/
│   │   ├── OutputFormat.swift
│   │   └── FileModels.swift
│   ├── Services/
│   │   ├── ConversionManager.swift
│   │   └── FileConverter.swift
│   └── Views/
│       └── SettingsView.swift
│
└── 📁 FormatConverter.xcodeproj/
```

---

## 🎯 Utilisation

1. **Sélectionnez le format de sortie** dans la sidebar gauche
2. **Ajoutez vos fichiers** via drag & drop ou le bouton "Parcourir"
3. **Cliquez sur "Convertir"**
4. **Récupérez vos fichiers** dans le dossier de sortie (Downloads par défaut)

### Exemples de conversions populaires

| De | Vers | Usage |
|----|------|-------|
| 📕 PDF | 📘 Word | Éditer un PDF |
| 🖼️ PNG | 📱 HEIC | Réduire la taille |
| 🎬 MOV | 📹 MP4 | Compatibilité web |
| 📦 RAR | 📁 Dossier | Extraire une archive |
| 🎵 WAV | 🎧 MP3 | Réduire la taille |

---

## ⚙️ Configuration

### Changer le dossier de sortie
Cliquez sur **"Changer"** à côté du dossier de sortie pour sélectionner un autre emplacement.

### Préférences (version Swift)
Accédez aux préférences via **⌘ + ,** pour :
- Choisir le dossier de sortie par défaut
- Activer/désactiver l'ouverture automatique du Finder
- Voir les outils installés

---

## 🔒 Sécurité & Confidentialité

- ✅ **100% local** - Aucune donnée envoyée sur internet
- ✅ **Open source** - Code vérifiable
- ✅ **Pas de tracking** - Aucune télémétrie
- ✅ **Fichiers originaux préservés** - Seules des copies sont créées

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

```bash
# Fork le projet
# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Commit
git commit -m "Ajout de ma fonctionnalité"

# Push
git push origin feature/ma-fonctionnalite

# Créer une Pull Request
```

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

---

## 👨‍💻 Auteur

Créé avec ❤️ par [@jbleroy75](https://github.com/jbleroy75)

---

<p align="center">
  <b>⭐ Star ce repo si tu trouves l'app utile !</b>
</p>
