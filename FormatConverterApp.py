#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format Converter - Version macOS Sonoma Style
Interface moderne avec design Apple
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil
from pathlib import Path
import threading
from typing import List, Tuple

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernDropZone(ctk.CTkFrame):
    """Zone de drop moderne avec animation"""
    
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.configure(
            fg_color=("#f5f5f7", "#1c1c1e"),
            corner_radius=16,
            border_width=2,
            border_color=("#e5e5e7", "#3a3a3c")
        )
        
        # Container central
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Icône
        self.icon_label = ctk.CTkLabel(
            self.inner,
            text="",
            font=ctk.CTkFont(size=56)
        )
        self.icon_label.pack(pady=(20, 15))
        
        # Texte principal
        self.title_label = ctk.CTkLabel(
            self.inner,
            text="Déposez vos fichiers ici",
            font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
            text_color=("#1d1d1f", "#f5f5f7")
        )
        self.title_label.pack(pady=(0, 5))
        
        # Sous-texte
        self.subtitle_label = ctk.CTkLabel(
            self.inner,
            text="ou cliquez pour parcourir vos fichiers",
            font=ctk.CTkFont(family="SF Pro Text", size=13),
            text_color=("#86868b", "#98989f")
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Bouton
        self.browse_btn = ctk.CTkButton(
            self.inner,
            text="Parcourir",
            font=ctk.CTkFont(family="SF Pro Text", size=14, weight="bold"),
            fg_color=("#007aff", "#0a84ff"),
            hover_color=("#0056b3", "#0070e0"),
            corner_radius=10,
            height=40,
            width=140,
            command=command
        )
        self.browse_btn.pack(pady=(0, 10))
        
        # Bind click sur toute la zone
        self.bind("<Button-1>", lambda e: command() if command else None)
        self.inner.bind("<Button-1>", lambda e: command() if command else None)
        for widget in [self.icon_label, self.title_label, self.subtitle_label]:
            widget.bind("<Button-1>", lambda e: command() if command else None)


class FormatButton(ctk.CTkButton):
    """Bouton de format style Apple"""
    
    def __init__(self, master, text, value, variable, icon="", **kwargs):
        self.value = value
        self.variable = variable
        
        super().__init__(
            master,
            text=f"  {icon}  {text}",
            font=ctk.CTkFont(family="SF Pro Text", size=13),
            fg_color="transparent",
            hover_color=("#e5e5e7", "#3a3a3c"),
            text_color=("#1d1d1f", "#f5f5f7"),
            anchor="w",
            height=36,
            corner_radius=8,
            command=self.select,
            **kwargs
        )
        
        self.variable.trace_add("write", self.update_state)
        self.update_state()
    
    def select(self):
        self.variable.set(self.value)
    
    def update_state(self, *args):
        if self.variable.get() == self.value:
            self.configure(
                fg_color=("#007aff", "#0a84ff"),
                text_color="#ffffff",
                hover_color=("#0056b3", "#0070e0")
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=("#1d1d1f", "#f5f5f7"),
                hover_color=("#e5e5e7", "#3a3a3c")
            )


class FileCard(ctk.CTkFrame):
    """Carte de fichier moderne"""
    
    def __init__(self, master, filename, size, icon, on_remove=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=("#ffffff", "#2c2c2e"),
            corner_radius=12,
            height=56
        )
        self.pack_propagate(False)
        
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=8)
        
        # Icône
        icon_label = ctk.CTkLabel(
            container,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=32
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Info fichier
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=filename[:40] + "..." if len(filename) > 40 else filename,
            font=ctk.CTkFont(family="SF Pro Text", size=13, weight="bold"),
            text_color=("#1d1d1f", "#f5f5f7"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        size_label = ctk.CTkLabel(
            info_frame,
            text=size,
            font=ctk.CTkFont(family="SF Pro Text", size=11),
            text_color=("#86868b", "#98989f"),
            anchor="w"
        )
        size_label.pack(anchor="w")
        
        # Bouton supprimer
        if on_remove:
            remove_btn = ctk.CTkButton(
                container,
                text="✕",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color=("#ff3b30", "#ff453a"),
                text_color=("#86868b", "#98989f"),
                width=28,
                height=28,
                corner_radius=14,
                command=on_remove
            )
            remove_btn.pack(side="right")


class FormatConverterApp(ctk.CTk):
    """Application principale"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration fenêtre
        self.title("Format Converter")
        self.geometry("1000x720")
        self.minsize(900, 600)
        
        # Variables
        self.files_to_convert: List[str] = []
        self.selected_format = ctk.StringVar(value="pdf")
        self.output_folder = Path.home() / "Downloads"
        self.file_cards: List[FileCard] = []
        
        # Configuration grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Créer l'interface
        self.create_sidebar()
        self.create_main_area()
        
    def create_sidebar(self):
        """Créer la sidebar style Apple"""
        
        # Sidebar container
        sidebar = ctk.CTkFrame(
            self,
            width=260,
            fg_color=("#f5f5f7", "#1c1c1e"),
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Titre app
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=60)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            title_frame,
            text="Format Converter",
            font=ctk.CTkFont(family="SF Pro Display", size=20, weight="bold"),
            text_color=("#1d1d1f", "#f5f5f7")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Convertissez tous vos fichiers",
            font=ctk.CTkFont(family="SF Pro Text", size=12),
            text_color=("#86868b", "#98989f")
        ).pack(anchor="w")
        
        # Scrollable frame pour les formats
        scroll_frame = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_button_color=("#d1d1d6", "#48484a"),
            scrollbar_button_hover_color=("#a1a1a6", "#636366")
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Catégories de formats
        categories = [
            ("DOCUMENTS", "📄", [
                ("PDF", "pdf", "📕"),
                ("Word", "docx", "📘"),
                ("Texte", "txt", "📝"),
                ("HTML", "html", "🌐"),
                ("Markdown", "md", "📋"),
            ]),
            ("IMAGES", "🖼️", [
                ("PNG", "png", "🖼️"),
                ("JPEG", "jpg", "📷"),
                ("HEIC", "heic", "📱"),
                ("WebP", "webp", "🌅"),
                ("GIF", "gif", "🎞️"),
                ("TIFF", "tiff", "🏞️"),
            ]),
            ("AUDIO", "🎵", [
                ("MP3", "mp3", "🎵"),
                ("WAV", "wav", "🔊"),
                ("AAC", "aac", "🎧"),
                ("FLAC", "flac", "💿"),
                ("M4A", "m4a", "🎶"),
            ]),
            ("VIDÉO", "🎬", [
                ("MP4", "mp4", "🎬"),
                ("MOV", "mov", "📹"),
                ("AVI", "avi", "📼"),
                ("MKV", "mkv", "🎥"),
                ("WebM", "webm", "🌐"),
            ]),
            ("ARCHIVES", "📦", [
                ("ZIP", "zip", "📦"),
                ("Extraire", "unzip", "📂"),
                ("TAR", "tar", "🗃️"),
                ("7Z", "7z", "🗜️"),
            ]),
        ]
        
        for cat_name, cat_icon, formats in categories:
            # Header catégorie
            header = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=30)
            header.pack(fill="x", pady=(15, 5), padx=5)
            
            ctk.CTkLabel(
                header,
                text=f"{cat_icon}  {cat_name}",
                font=ctk.CTkFont(family="SF Pro Text", size=11, weight="bold"),
                text_color=("#86868b", "#98989f")
            ).pack(anchor="w")
            
            # Boutons de format
            for name, value, icon in formats:
                btn = FormatButton(
                    scroll_frame,
                    text=name,
                    value=value,
                    variable=self.selected_format,
                    icon=icon
                )
                btn.pack(fill="x", pady=2, padx=5)
        
        # Footer avec output folder
        footer = ctk.CTkFrame(sidebar, fg_color="transparent", height=80)
        footer.pack(fill="x", padx=15, pady=15)
        footer.pack_propagate(False)
        
        ctk.CTkLabel(
            footer,
            text="📂 Dossier de sortie",
            font=ctk.CTkFont(family="SF Pro Text", size=11, weight="bold"),
            text_color=("#86868b", "#98989f")
        ).pack(anchor="w")
        
        output_frame = ctk.CTkFrame(footer, fg_color="transparent")
        output_frame.pack(fill="x", pady=(5, 0))
        
        self.output_label = ctk.CTkLabel(
            output_frame,
            text="Downloads",
            font=ctk.CTkFont(family="SF Pro Text", size=12),
            text_color=("#1d1d1f", "#f5f5f7"),
            anchor="w"
        )
        self.output_label.pack(side="left")
        
        ctk.CTkButton(
            output_frame,
            text="Changer",
            font=ctk.CTkFont(family="SF Pro Text", size=11),
            fg_color="transparent",
            hover_color=("#e5e5e7", "#3a3a3c"),
            text_color=("#007aff", "#0a84ff"),
            width=60,
            height=24,
            corner_radius=6,
            command=self.change_output_folder
        ).pack(side="right")
    
    def create_main_area(self):
        """Créer la zone principale"""
        
        main = ctk.CTkFrame(self, fg_color=("#ffffff", "#000000"), corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        
        # Padding container
        container = ctk.CTkFrame(main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=25)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Zone de drop
        self.drop_zone = ModernDropZone(
            container,
            command=self.browse_files,
            height=200
        )
        self.drop_zone.pack(fill="x", pady=(0, 20))
        
        # Section fichiers
        files_section = ctk.CTkFrame(container, fg_color="transparent")
        files_section.pack(fill="both", expand=True)
        
        # Header fichiers
        files_header = ctk.CTkFrame(files_section, fg_color="transparent", height=40)
        files_header.pack(fill="x")
        files_header.pack_propagate(False)
        
        ctk.CTkLabel(
            files_header,
            text="Fichiers sélectionnés",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            text_color=("#1d1d1f", "#f5f5f7")
        ).pack(side="left")
        
        self.file_count_label = ctk.CTkLabel(
            files_header,
            text="0 fichier",
            font=ctk.CTkFont(family="SF Pro Text", size=13),
            text_color=("#86868b", "#98989f")
        )
        self.file_count_label.pack(side="left", padx=(10, 0))
        
        self.clear_btn = ctk.CTkButton(
            files_header,
            text="Tout effacer",
            font=ctk.CTkFont(family="SF Pro Text", size=12),
            fg_color="transparent",
            hover_color=("#ffeceb", "#3a2c2b"),
            text_color=("#ff3b30", "#ff453a"),
            width=100,
            height=28,
            corner_radius=6,
            command=self.clear_files
        )
        self.clear_btn.pack(side="right")
        
        # Liste des fichiers scrollable
        self.files_scroll = ctk.CTkScrollableFrame(
            files_section,
            fg_color=("#f5f5f7", "#1c1c1e"),
            corner_radius=12,
            scrollbar_button_color=("#d1d1d6", "#48484a")
        )
        self.files_scroll.pack(fill="both", expand=True, pady=(10, 20))
        
        # Message vide
        self.empty_label = ctk.CTkLabel(
            self.files_scroll,
            text="Aucun fichier sélectionné\nCliquez sur 'Parcourir' pour ajouter des fichiers",
            font=ctk.CTkFont(family="SF Pro Text", size=14),
            text_color=("#86868b", "#98989f"),
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=40)
        
        # Bouton convertir
        self.convert_btn = ctk.CTkButton(
            container,
            text="Convertir",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            fg_color=("#007aff", "#0a84ff"),
            hover_color=("#0056b3", "#0070e0"),
            height=50,
            corner_radius=12,
            command=self.start_conversion
        )
        self.convert_btn.pack(fill="x")
        
        # Progress bar (hidden by default)
        self.progress = ctk.CTkProgressBar(
            container,
            fg_color=("#e5e5e7", "#3a3a3c"),
            progress_color=("#007aff", "#0a84ff"),
            height=4,
            corner_radius=2
        )
        
    def browse_files(self):
        """Ouvrir le sélecteur de fichiers"""
        files = filedialog.askopenfilenames(
            title="Sélectionnez les fichiers à convertir",
            filetypes=[
                ("Tous les fichiers", "*.*"),
                ("Documents", "*.pdf *.docx *.doc *.txt *.rtf *.html *.md"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.webp *.tiff *.bmp *.heic"),
                ("Audio", "*.mp3 *.wav *.aac *.flac *.ogg *.m4a"),
                ("Vidéo", "*.mp4 *.mov *.avi *.mkv *.webm *.wmv"),
                ("Archives", "*.zip *.tar *.gz *.7z *.rar"),
            ]
        )
        
        for f in files:
            if f not in self.files_to_convert:
                self.files_to_convert.append(f)
                self.add_file_card(f)
        
        self.update_file_count()
    
    def add_file_card(self, filepath):
        """Ajouter une carte de fichier"""
        self.empty_label.pack_forget()
        
        path = Path(filepath)
        size = self.format_size(path.stat().st_size)
        icon = self.get_file_icon(path.suffix.lower())
        
        card = FileCard(
            self.files_scroll,
            filename=path.name,
            size=size,
            icon=icon,
            on_remove=lambda p=filepath: self.remove_file(p)
        )
        card.pack(fill="x", pady=4, padx=4)
        self.file_cards.append((filepath, card))
    
    def remove_file(self, filepath):
        """Supprimer un fichier de la liste"""
        self.files_to_convert.remove(filepath)
        for f, card in self.file_cards:
            if f == filepath:
                card.destroy()
                self.file_cards.remove((f, card))
                break
        
        self.update_file_count()
        
        if not self.files_to_convert:
            self.empty_label.pack(expand=True, pady=40)
    
    def clear_files(self):
        """Effacer tous les fichiers"""
        self.files_to_convert.clear()
        for _, card in self.file_cards:
            card.destroy()
        self.file_cards.clear()
        self.update_file_count()
        self.empty_label.pack(expand=True, pady=40)
    
    def update_file_count(self):
        """Mettre à jour le compteur de fichiers"""
        count = len(self.files_to_convert)
        text = f"{count} fichier{'s' if count > 1 else ''}"
        self.file_count_label.configure(text=text)
    
    def change_output_folder(self):
        """Changer le dossier de sortie"""
        folder = filedialog.askdirectory(title="Choisir le dossier de sortie")
        if folder:
            self.output_folder = Path(folder)
            self.output_label.configure(text=self.output_folder.name)
    
    def start_conversion(self):
        """Démarrer la conversion"""
        if not self.files_to_convert:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné !")
            return
        
        # Afficher la progress bar
        self.convert_btn.configure(text="Conversion en cours...", state="disabled")
        self.progress.pack(fill="x", pady=(10, 0))
        self.progress.set(0)
        
        format_out = self.selected_format.get()
        thread = threading.Thread(target=self.convert_files, args=(format_out,))
        thread.start()
    
    def convert_files(self, format_out):
        """Convertir les fichiers (thread séparé)"""
        success = 0
        errors = []
        total = len(self.files_to_convert)
        
        for i, file_path in enumerate(self.files_to_convert):
            try:
                self.convert_single_file(file_path, format_out)
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
            
            # Update progress
            self.after(0, lambda p=(i+1)/total: self.progress.set(p))
        
        # Afficher résultat
        self.after(0, lambda: self.show_result(success, errors))
    
    def convert_single_file(self, input_path, format_out):
        """Convertir un fichier"""
        input_path = Path(input_path)
        input_ext = input_path.suffix.lower()[1:]
        output_name = input_path.stem
        
        # Décompression
        if format_out == "unzip":
            output_dir = self.output_folder / output_name
            output_dir.mkdir(exist_ok=True)
            
            if input_ext == "zip":
                subprocess.run(["unzip", "-o", str(input_path), "-d", str(output_dir)], 
                             check=True, capture_output=True)
            elif input_ext in ["tar", "gz", "tgz"]:
                subprocess.run(["tar", "-xf", str(input_path), "-C", str(output_dir)], 
                             check=True, capture_output=True)
            elif input_ext == "7z":
                subprocess.run(["7z", "x", str(input_path), f"-o{output_dir}"], 
                             check=True, capture_output=True)
            elif input_ext == "rar":
                subprocess.run(["unar", "-o", str(output_dir), str(input_path)], 
                             check=True, capture_output=True)
            return
        
        output_path = self.output_folder / f"{output_name}.{format_out}"
        
        # Éviter les conflits
        counter = 1
        while output_path.exists():
            output_path = self.output_folder / f"{output_name} ({counter}).{format_out}"
            counter += 1
        
        # Images
        if format_out in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "webp", "heic"]:
            if format_out == "webp":
                subprocess.run(["cwebp", str(input_path), "-o", str(output_path)], 
                             check=True, capture_output=True)
            elif format_out == "heic":
                subprocess.run(["sips", "-s", "format", "heic", str(input_path), 
                              "--out", str(output_path)], check=True, capture_output=True)
            else:
                subprocess.run(["sips", "-s", "format", format_out, str(input_path), 
                              "--out", str(output_path)], check=True, capture_output=True)
        
        # Audio/Vidéo
        elif format_out in ["mp3", "wav", "aac", "flac", "m4a", "mp4", "mov", "avi", "mkv", "webm"]:
            cmd = ["ffmpeg", "-i", str(input_path), "-y"]
            
            if format_out == "mp3":
                cmd += ["-codec:a", "libmp3lame", "-qscale:a", "2"]
            elif format_out == "wav":
                cmd += ["-codec:a", "pcm_s16le"]
            elif format_out == "flac":
                cmd += ["-codec:a", "flac"]
            elif format_out in ["aac", "m4a"]:
                cmd += ["-codec:a", "aac", "-b:a", "256k"]
            elif format_out == "mp4":
                cmd += ["-codec:v", "libx264", "-preset", "medium", "-crf", "23", 
                       "-codec:a", "aac", "-b:a", "128k"]
            elif format_out == "webm":
                cmd += ["-codec:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
                       "-codec:a", "libopus"]
            elif format_out == "mov":
                cmd += ["-codec:v", "prores_ks", "-profile:v", "3"]
            elif format_out == "avi":
                cmd += ["-codec:v", "mpeg4", "-q:v", "5"]
            elif format_out == "mkv":
                cmd += ["-codec:v", "copy", "-codec:a", "copy"]
            
            cmd.append(str(output_path))
            subprocess.run(cmd, check=True, capture_output=True)
        
        # Image vers PDF
        elif format_out == "pdf" and input_ext in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "webp", "heic"]:
            from PIL import Image
            img = Image.open(str(input_path))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(str(output_path), "PDF", resolution=100.0)
        
        # Documents
        elif format_out in ["pdf", "docx", "html", "md", "txt"]:
            soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            
            # PDF vers autre format
            if input_ext == "pdf":
                if format_out == "docx" and os.path.exists(soffice):
                    subprocess.run([
                        soffice, "--headless", "--infilter=writer_pdf_import",
                        "--convert-to", "docx",
                        "--outdir", str(self.output_folder),
                        str(input_path)
                    ], check=True, capture_output=True)
                elif format_out == "txt":
                    subprocess.run(["pdftotext", str(input_path), str(output_path)], 
                                 check=True, capture_output=True)
                else:
                    raise Exception(f"Conversion PDF → {format_out} non supportée")
            
            # Vers PDF (documents)
            elif format_out == "pdf":
                if os.path.exists(soffice) and input_ext in ["docx", "doc", "odt", "rtf", "txt"]:
                    subprocess.run([
                        soffice, "--headless",
                        "--convert-to", "pdf",
                        "--outdir", str(self.output_folder),
                        str(input_path)
                    ], check=True, capture_output=True)
                elif shutil.which("pandoc"):
                    subprocess.run(["pandoc", str(input_path), "-o", str(output_path)], 
                                 check=True, capture_output=True)
            
            # Autres avec Pandoc
            elif shutil.which("pandoc"):
                subprocess.run(["pandoc", str(input_path), "-o", str(output_path)], 
                             check=True, capture_output=True)
        
        # Archives
        elif format_out == "zip":
            subprocess.run(["zip", "-r", str(output_path), str(input_path)], 
                         check=True, capture_output=True)
        elif format_out == "tar":
            subprocess.run(["tar", "-cvf", str(output_path), "-C", 
                          str(input_path.parent), input_path.name], 
                         check=True, capture_output=True)
        elif format_out == "7z":
            subprocess.run(["7z", "a", str(output_path), str(input_path)], 
                         check=True, capture_output=True)
    
    def show_result(self, success, errors):
        """Afficher le résultat de la conversion"""
        self.convert_btn.configure(text="Convertir", state="normal")
        self.progress.pack_forget()
        self.clear_files()
        
        if errors:
            message = f"✅ {success} fichier(s) converti(s)\n\n❌ Erreurs:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... et {len(errors) - 5} autre(s)"
            messagebox.showwarning("Conversion terminée", message)
        else:
            result = messagebox.askyesno(
                "Succès ! 🎉", 
                f"✅ {success} fichier(s) converti(s) avec succès !\n\nOuvrir le dossier de sortie ?"
            )
            if result:
                subprocess.run(["open", str(self.output_folder)])
    
    @staticmethod
    def format_size(size_bytes):
        """Formater la taille du fichier"""
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} To"
    
    @staticmethod
    def get_file_icon(ext):
        """Obtenir l'icône du fichier selon l'extension"""
        icons = {
            ".pdf": "📕", ".docx": "📘", ".doc": "📘", ".txt": "📝",
            ".rtf": "📄", ".html": "🌐", ".md": "📋",
            ".png": "🖼️", ".jpg": "📷", ".jpeg": "📷", ".gif": "🎞️",
            ".webp": "🌅", ".tiff": "🏞️", ".bmp": "🎨", ".heic": "📸",
            ".mp3": "🎵", ".wav": "🔊", ".aac": "🎧", ".flac": "💿",
            ".m4a": "🎶", ".ogg": "🎼",
            ".mp4": "🎬", ".mov": "📹", ".avi": "📼", ".mkv": "🎥",
            ".webm": "🌐", ".wmv": "📺",
            ".zip": "📦", ".tar": "🗃️", ".gz": "🗜️", ".7z": "📦", ".rar": "📦",
            ".json": "📊", ".csv": "📈", ".xml": "📋",
        }
        return icons.get(ext, "📄")


def main():
    app = FormatConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
