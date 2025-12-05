# 🔄 Format Converter 2.0

<p align="center">
  <img src="icons/AppIcon.png" alt="Format Converter" width="128" height="128">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/macOS-13.0+-blue.svg" alt="macOS">
  <img src="https://img.shields.io/badge/Python-3.9+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/Swift-5.9-orange.svg" alt="Swift">
  <img src="https://img.shields.io/badge/Version-2.0-green.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
</p>

<p align="center">
  <b>🚀 Application macOS complète pour convertir tous types de fichiers</b><br>
  Documents • Images • Audio • Vidéo • Archives • Données
</p>

---

## ✨ Nouveautés v2.0

| Fonctionnalité | Description |
|----------------|-------------|
| 🖼️ **Prévisualisation** | Aperçu des images, textes et PDFs avant conversion |
| 📊 **Progression détaillée** | Barre de progression fichier par fichier |
| ⚙️ **Options avancées** | Qualité, redimensionnement, bitrate, préfixe/suffixe |
| 📋 **Historique** | Log de toutes vos conversions |
| 📄 **Outils PDF** | Fusionner, diviser, compresser des PDFs |
| 🔊 **Extraire audio** | Extraire la piste audio d'une vidéo |
| ⌨️ **Raccourcis** | ⌘O ouvrir, ⌘↵ convertir, ⌘H historique |
| 🔔 **Notifications** | Alertes macOS à la fin des conversions |
| 🎨 **Icône personnalisée** | Belle icône pour votre Dock |

---

## 📸 Captures d'écran

### Interface principale

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         🔄 Format Converter v2.0                              │
├────────────────┬───────────────────────────────────────┬─────────────────────┤
│  FORMAT        │                                       │  Prévisualisation   │
│                │         📁                            │  ┌───────────────┐  │
│  DOCUMENTS     │                                       │  │               │  │
│   ● PDF        │    Déposez vos fichiers ici          │  │   [Aperçu]    │  │
│   ○ Word       │    ou cliquez pour parcourir         │  │               │  │
│   ○ Texte      │                                       │  └───────────────┘  │
│                │        [ Parcourir ]                  │                     │
│  IMAGES        │                                       │  ⚙️ Options          │
│   ○ PNG        ├───────────────────────────────────────┤  Qualité: [85%]    │
│   ○ JPEG       │  Fichiers                  3 fichiers │  Resize: [Original]│
│   ○ HEIC       │  ┌─────────────────────────────────┐  │  Bitrate: [256k]   │
│   ○ WebP       │  │ 📷 photo.jpg          2.3 Mo  ✕ │  │                     │
│                │  │ 📕 document.pdf       156 Ko  ✕ │  │  ☑ Conserver ratio │
│  AUDIO         │  │ 🎬 video.mp4          45 Mo   ✕ │  │                     │
│   ○ MP3        │  └─────────────────────────────────┘  │  ┌───────────────┐  │
│   ○ WAV        │                                       │  │ 📄 Outils PDF │  │
│                │  ┌─────────────────────────────────┐  │  └───────────────┘  │
│  VIDÉO         │  │       🔄 Convertir • ⌘↵         │  │  ┌───────────────┐  │
│   ○ MP4        │  └─────────────────────────────────┘  │  │ 📋 Historique │  │
│   ○ MOV        │                                       │  └───────────────┘  │
│                │                                       │                     │
│  📂 Downloads  │                                       │                     │
└────────────────┴───────────────────────────────────────┴─────────────────────┘
```

### Fenêtre de progression

```
┌─────────────────────────────────────────────────┐
│         Conversion de 5 fichier(s)              │
├─────────────────────────────────────────────────┤
│  Progression globale:                           │
│  ████████████████░░░░░░░░░░░░░░  60%           │
│                                                 │
│  Fichier en cours:                              │
│  video.mp4                                      │
│  ████████░░░░░░░░░░░░░░░░░░░░░░                │
│                                                 │
│  ✅ photo1.jpg                                  │
│  ✅ photo2.png                                  │
│  ✅ document.pdf                                │
│  🔄 video.mp4                                   │
│                                                 │
│              [ Annuler ]                        │
└─────────────────────────────────────────────────┘
```

### Outils PDF

```
┌─────────────────────────────────────────────────┐
│               Outils PDF                        │
├─────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬────────────┐          │
│  │ Fusionner│ Diviser  │ Compresser │          │
│  └──────────┴──────────┴────────────┘          │
│                                                 │
│  Fusionner plusieurs PDF en un seul            │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ document1.pdf                       │       │
│  │ document2.pdf                       │       │
│  │ document3.pdf                       │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  [Ajouter des PDF]        [Fusionner]          │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Formats supportés

### 📄 Documents
| Format | Extension | Lecture | Écriture |
|--------|-----------|---------|----------|
| PDF | `.pdf` | ✅ | ✅ |
| Word | `.docx` `.doc` | ✅ | ✅ |
| Texte | `.txt` | ✅ | ✅ |
| HTML | `.html` | ✅ | ✅ |
| Markdown | `.md` | ✅ | ✅ |
| Rich Text | `.rtf` | ✅ | ✅ |

### 🖼️ Images
| Format | Extension | Qualité ajustable | Resize |
|--------|-----------|-------------------|--------|
| PNG | `.png` | - | ✅ |
| JPEG | `.jpg` | ✅ 1-100% | ✅ |
| HEIC | `.heic` | ✅ | ✅ |
| WebP | `.webp` | ✅ 1-100% | ✅ |
| GIF | `.gif` | - | ✅ |
| TIFF | `.tiff` | - | ✅ |

### 🎵 Audio
| Format | Extension | Bitrate |
|--------|-----------|---------|
| MP3 | `.mp3` | 128k-320k |
| WAV | `.wav` | Lossless |
| AAC | `.aac` | 128k-320k |
| FLAC | `.flac` | Lossless |
| M4A | `.m4a` | 128k-320k |

### 🎬 Vidéo
| Format | Extension | Codec |
|--------|-----------|-------|
| MP4 | `.mp4` | H.264 |
| MOV | `.mov` | ProRes |
| AVI | `.avi` | MPEG-4 |
| MKV | `.mkv` | Copy |
| WebM | `.webm` | VP9 |

### 📦 Archives
| Format | Extension | Mot de passe |
|--------|-----------|--------------|
| ZIP | `.zip` | Bientôt |
| TAR | `.tar` | - |
| 7Z | `.7z` | Bientôt |
| RAR | `.rar` | Lecture |

---

## 🚀 Installation

### Prérequis
- macOS 13.0 (Ventura) ou supérieur
- Python 3.9+

### Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/jbleroy75/FormatConverter.git
cd FormatConverter

# 2. Installer les dépendances
pip3 install customtkinter Pillow pypdf

# 3. Installer les outils de conversion (optionnel mais recommandé)
./install-tools.sh

# 4. Lancer l'application
python3 FormatConverterApp.py
```

### Outils recommandés

```bash
# Via Homebrew
brew install ffmpeg      # Audio/Vidéo
brew install pandoc      # Documents
brew install p7zip       # Archives 7z
brew install unar        # Archives RAR
brew install webp        # Images WebP
brew install ghostscript # Compression PDF

# LibreOffice (pour Word/Excel)
brew install --cask libreoffice
```

---

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `⌘ + O` | Ouvrir des fichiers |
| `⌘ + ↵` | Lancer la conversion |
| `⌘ + H` | Afficher l'historique |
| `⌘ + ,` | Options |
| `⌫` | Effacer la sélection |

---

## 📁 Structure du projet

```
FormatConverter/
├── 🐍 FormatConverterApp.py    # Application Python principale
├── 🛠️ install-tools.sh         # Script d'installation
├── 📄 README.md
├── 📜 LICENSE
│
├── 🎨 icons/                    # Icônes de l'application
│   ├── AppIcon.png
│   ├── icon_512x512.png
│   └── ...
│
├── 📱 FormatConverter/          # Version Swift/Xcode
│   ├── FormatConverterApp.swift
│   ├── ContentView.swift
│   ├── Models/
│   ├── Services/
│   └── Views/
│
└── 📦 FormatConverter.xcodeproj/
```

---

## 🔒 Sécurité & Confidentialité

- ✅ **100% local** - Aucune donnée envoyée sur internet
- ✅ **Open source** - Code entièrement vérifiable
- ✅ **Pas de tracking** - Aucune télémétrie ni analytics
- ✅ **Fichiers préservés** - Les originaux ne sont jamais modifiés

---

## 🤝 Contribution

Les contributions sont les bienvenues !

```bash
# Fork, clone, branch
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester
python3 FormatConverterApp.py

# Commit et PR
git commit -m "✨ Ajout de nouvelle fonctionnalité"
git push origin feature/nouvelle-fonctionnalite
```

---

## 📝 Changelog

### v2.0.0 (2024)
- ✨ Prévisualisation des fichiers
- ✨ Barre de progression détaillée
- ✨ Options de qualité/compression/resize
- ✨ Historique des conversions
- ✨ Outils PDF (fusionner/diviser/compresser)
- ✨ Extraction audio de vidéo
- ✨ Raccourcis clavier
- ✨ Notifications système
- ✨ Icône personnalisée
- 🎨 Nouveau design moderne

### v1.0.0 (2024)
- 🎉 Version initiale

---

## 📜 Licence

MIT License - Voir [LICENSE](LICENSE)

---

<p align="center">
  Créé avec ❤️ par <a href="https://github.com/jbleroy75">@jbleroy75</a>
</p>

<p align="center">
  <b>⭐ Star ce repo si vous trouvez l'app utile !</b>
</p>
