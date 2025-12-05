#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format Converter 2.1 - Design épuré style Apple
Interface minimaliste avec couleurs sobres
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import subprocess
import os
import shutil
import json
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable

# === THÈME PERSONNALISÉ ===
class Theme:
    """Palette de couleurs sobre et élégante"""
    # Backgrounds
    BG_PRIMARY = ("#FAFAFA", "#141414")
    BG_SECONDARY = ("#FFFFFF", "#1C1C1E")
    BG_TERTIARY = ("#F2F2F7", "#2C2C2E")
    BG_CARD = ("#FFFFFF", "#1C1C1E")
    
    # Textes
    TEXT_PRIMARY = ("#1D1D1F", "#F5F5F7")
    TEXT_SECONDARY = ("#86868B", "#98989F")
    TEXT_TERTIARY = ("#AEAEB2", "#636366")
    
    # Accents
    ACCENT = ("#007AFF", "#0A84FF")
    ACCENT_HOVER = ("#0056B3", "#0070E0")
    SUCCESS = ("#34C759", "#32D74B")
    WARNING = ("#FF9500", "#FF9F0A")
    DANGER = ("#FF3B30", "#FF453A")
    
    # Bordures
    BORDER = ("#E5E5EA", "#38383A")
    BORDER_LIGHT = ("#F2F2F7", "#2C2C2E")
    
    # Ombres
    SHADOW = ("#00000010", "#00000040")

# Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HISTORY_FILE = Path.home() / ".format_converter_history.json"


class ConversionOptions:
    """Options de conversion"""
    def __init__(self):
        self.quality = 85
        self.resize_width = None
        self.resize_height = None
        self.keep_aspect_ratio = True
        self.bitrate_audio = "256k"
        self.prefix = ""
        self.suffix = ""


class ConversionHistory:
    """Gestionnaire d'historique"""
    
    @staticmethod
    def load() -> List[Dict]:
        if HISTORY_FILE.exists():
            try:
                return json.load(open(HISTORY_FILE, 'r'))
            except:
                return []
        return []
    
    @staticmethod
    def save(history: List[Dict]):
        json.dump(history[-50:], open(HISTORY_FILE, 'w'), indent=2, default=str)
    
    @staticmethod
    def add(input_file: str, output_file: str, format_out: str, success: bool):
        history = ConversionHistory.load()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "input": input_file,
            "output": output_file,
            "format": format_out,
            "success": success
        })
        ConversionHistory.save(history)


# === COMPOSANTS UI PERSONNALISÉS ===

class SidebarButton(ctk.CTkButton):
    """Bouton de sidebar élégant"""
    
    def __init__(self, master, text, value, variable, icon="", **kwargs):
        self.value = value
        self.variable = variable
        
        super().__init__(
            master,
            text=f"{icon}  {text}" if icon else text,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color="transparent",
            hover_color=Theme.BG_TERTIARY,
            text_color=Theme.TEXT_PRIMARY,
            text_color_disabled=Theme.TEXT_TERTIARY,
            anchor="w",
            height=44,
            corner_radius=10,
            border_spacing=16,
            command=self._select,
            **kwargs
        )
        
        self.variable.trace_add("write", self._update_state)
        self._update_state()
    
    def _select(self):
        self.variable.set(self.value)
    
    def _update_state(self, *args):
        if self.variable.get() == self.value:
            self.configure(
                fg_color=Theme.ACCENT,
                text_color="#FFFFFF",
                hover_color=Theme.ACCENT_HOVER,
                font=ctk.CTkFont(size=14, weight="bold")
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=Theme.TEXT_PRIMARY,
                hover_color=Theme.BG_TERTIARY,
                font=ctk.CTkFont(size=14, weight="normal")
            )


class FileItem(ctk.CTkFrame):
    """Item de fichier avec design épuré"""
    
    def __init__(self, master, filepath: str, on_remove: Callable, on_select: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.filepath = filepath
        self.selected = False
        
        self.configure(
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            height=68
        )
        self.pack_propagate(False)
        
        path = Path(filepath)
        
        # Container interne
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)
        
        # Icône avec fond coloré
        icon_frame = ctk.CTkFrame(
            inner,
            fg_color=self._get_icon_bg(path.suffix.lower()),
            corner_radius=10,
            width=42,
            height=42
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=self._get_icon(path.suffix.lower()),
            font=ctk.CTkFont(size=18)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Infos fichier
        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=14)
        
        # Nom (tronqué si nécessaire)
        name = path.name
        if len(name) > 32:
            name = name[:29] + "..."
        
        self.name_label = ctk.CTkLabel(
            info,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.name_label.pack(anchor="w")
        
        # Taille + extension
        try:
            size = self._format_size(path.stat().st_size)
            ext = path.suffix.upper()[1:] if path.suffix else "FILE"
            subtitle = f"{ext} • {size}"
        except:
            subtitle = path.suffix.upper()[1:] if path.suffix else "FILE"
        
        self.size_label = ctk.CTkLabel(
            info,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.size_label.pack(anchor="w", pady=(2, 0))
        
        # Bouton supprimer (discret)
        self.remove_btn = ctk.CTkButton(
            inner,
            text="✕",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            hover_color=("#FFEBEE", "#3D1F1F"),
            text_color=Theme.TEXT_TERTIARY,
            font=ctk.CTkFont(size=14),
            command=lambda: on_remove(filepath)
        )
        self.remove_btn.pack(side="right", padx=(8, 0))
        
        # Bindings
        for widget in [self, inner, info, self.name_label, self.size_label]:
            widget.bind("<Button-1>", lambda e: on_select(filepath))
            widget.bind("<Enter>", self._on_hover)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_hover(self, event):
        self.configure(border_color=Theme.ACCENT)
    
    def _on_leave(self, event):
        self.configure(border_color=Theme.BORDER_LIGHT)
    
    def set_selected(self, selected: bool):
        self.selected = selected
        if selected:
            self.configure(
                border_color=Theme.ACCENT,
                border_width=2
            )
        else:
            self.configure(
                border_color=Theme.BORDER_LIGHT,
                border_width=1
            )
    
    @staticmethod
    def _get_icon(ext: str) -> str:
        icons = {
            ".pdf": "📄", ".docx": "📝", ".doc": "📝", ".txt": "📃",
            ".png": "🖼", ".jpg": "📷", ".jpeg": "📷", ".gif": "🎞",
            ".heic": "📱", ".webp": "🌄", ".tiff": "🏞",
            ".mp3": "🎵", ".wav": "🔊", ".aac": "🎧", ".flac": "💿",
            ".mp4": "🎬", ".mov": "📹", ".avi": "📼", ".mkv": "🎥",
            ".zip": "📦", ".rar": "📦", ".7z": "📦", ".tar": "🗃",
            ".json": "📊", ".csv": "📈", ".xml": "📋"
        }
        return icons.get(ext, "📄")
    
    @staticmethod
    def _get_icon_bg(ext: str) -> tuple:
        colors = {
            ".pdf": ("#FFEBEE", "#3D1F1F"),
            ".docx": ("#E3F2FD", "#1F2D3D"),
            ".doc": ("#E3F2FD", "#1F2D3D"),
            ".txt": ("#F3E5F5", "#2D1F3D"),
            ".png": ("#E8F5E9", "#1F3D1F"),
            ".jpg": ("#FFF3E0", "#3D2D1F"),
            ".jpeg": ("#FFF3E0", "#3D2D1F"),
            ".mp3": ("#F3E5F5", "#2D1F3D"),
            ".mp4": ("#FFF8E1", "#3D351F"),
            ".zip": ("#EFEBE9", "#2D2A28"),
        }
        return colors.get(ext, ("#F5F5F5", "#2C2C2E"))
    
    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"


class PreviewCard(ctk.CTkFrame):
    """Carte de prévisualisation élégante"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=16, pady=(12, 0))
        
        ctk.CTkLabel(
            header,
            text="Aperçu",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Zone de prévisualisation
        self.preview_area = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_TERTIARY,
            corner_radius=8,
            height=160
        )
        self.preview_area.pack(fill="x", padx=16, pady=12)
        self.preview_area.pack_propagate(False)
        
        self.preview_content = ctk.CTkLabel(
            self.preview_area,
            text="Sélectionnez un fichier",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_TERTIARY
        )
        self.preview_content.pack(expand=True)
        
        # Infos
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        self.filename_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.filename_label.pack(anchor="w")
        
        self.details_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_SECONDARY
        )
        self.details_label.pack(anchor="w")
        
        self.current_image = None
    
    def show(self, filepath: str):
        """Afficher l'aperçu d'un fichier"""
        path = Path(filepath)
        ext = path.suffix.lower()
        
        self.filename_label.configure(text=path.name[:30] + ("..." if len(path.name) > 30 else ""))
        
        try:
            size = self._format_size(path.stat().st_size)
            self.details_label.configure(text=f"{ext.upper()[1:]} • {size}")
        except:
            self.details_label.configure(text=ext.upper()[1:])
        
        # Prévisualisation selon type
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
            self._show_image(filepath)
        elif ext in ['.txt', '.md', '.json', '.xml', '.csv', '.yaml']:
            self._show_text(filepath)
        else:
            self._show_icon(ext)
    
    def _show_image(self, filepath: str):
        try:
            img = Image.open(filepath)
            # Resize pour aperçu
            img.thumbnail((200, 140), Image.Resampling.LANCZOS)
            self.current_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.preview_content.configure(image=self.current_image, text="")
            
            # Dimensions originales
            orig = Image.open(filepath)
            self.details_label.configure(
                text=f"{orig.width} × {orig.height} px • {self._format_size(Path(filepath).stat().st_size)}"
            )
        except:
            self._show_icon(Path(filepath).suffix.lower())
    
    def _show_text(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                preview = f.read(200)
            if len(preview) == 200:
                preview += "..."
            self.preview_content.configure(image=None, text=preview[:150])
        except:
            self.preview_content.configure(image=None, text="Impossible de lire")
    
    def _show_icon(self, ext: str):
        icons = {
            ".pdf": "📄", ".mp3": "🎵", ".mp4": "🎬", ".zip": "📦"
        }
        icon = icons.get(ext, "📄")
        self.preview_content.configure(image=None, text=icon, font=ctk.CTkFont(size=48))
    
    def clear(self):
        self.preview_content.configure(image=None, text="Sélectionnez un fichier", font=ctk.CTkFont(size=12))
        self.filename_label.configure(text="")
        self.details_label.configure(text="")
        self.current_image = None
    
    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"


class OptionsCard(ctk.CTkFrame):
    """Carte d'options avec design épuré"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        self.options = ConversionOptions()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=16, pady=(12, 0))
        
        ctk.CTkLabel(
            header,
            text="Options",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Contenu
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=12)
        
        # Qualité
        self._create_option_row(content, "Qualité", self._create_quality_control)
        
        # Resize
        self._create_option_row(content, "Taille", self._create_resize_control)
        
        # Bitrate
        self._create_option_row(content, "Bitrate", self._create_bitrate_control)
    
    def _create_option_row(self, parent, label: str, control_factory):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=36)
        row.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=Theme.TEXT_PRIMARY,
            width=70,
            anchor="w"
        ).pack(side="left")
        
        control_factory(row)
    
    def _create_quality_control(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="right", fill="x", expand=True)
        
        self.quality_label = ctk.CTkLabel(
            frame,
            text="85%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.ACCENT,
            width=40
        )
        self.quality_label.pack(side="right")
        
        self.quality_slider = ctk.CTkSlider(
            frame,
            from_=10,
            to=100,
            number_of_steps=90,
            height=16,
            button_color=Theme.ACCENT[1],
            button_hover_color=Theme.ACCENT_HOVER[1],
            progress_color=Theme.ACCENT[1],
            command=self._on_quality_change
        )
        self.quality_slider.set(85)
        self.quality_slider.pack(side="right", fill="x", expand=True, padx=(0, 10))
    
    def _create_resize_control(self, parent):
        self.resize_var = ctk.StringVar(value="Original")
        
        menu = ctk.CTkOptionMenu(
            parent,
            values=["Original", "1920×1080", "1280×720", "800×600", "640×480"],
            variable=self.resize_var,
            width=120,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=Theme.BG_TERTIARY,
            button_color=Theme.BG_TERTIARY,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_SECONDARY,
            corner_radius=6
        )
        menu.pack(side="right")
    
    def _create_bitrate_control(self, parent):
        self.bitrate_var = ctk.StringVar(value="256k")
        
        menu = ctk.CTkOptionMenu(
            parent,
            values=["128k", "192k", "256k", "320k"],
            variable=self.bitrate_var,
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=Theme.BG_TERTIARY,
            button_color=Theme.BG_TERTIARY,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_SECONDARY,
            corner_radius=6
        )
        menu.pack(side="right")
    
    def _on_quality_change(self, value):
        self.quality_label.configure(text=f"{int(value)}%")
        self.options.quality = int(value)
    
    def get_options(self) -> ConversionOptions:
        self.options.quality = int(self.quality_slider.get())
        self.options.bitrate_audio = self.bitrate_var.get()
        
        resize = self.resize_var.get()
        if resize != "Original" and "×" in resize:
            w, h = resize.split("×")
            self.options.resize_width = int(w)
            self.options.resize_height = int(h)
        else:
            self.options.resize_width = None
            self.options.resize_height = None
        
        return self.options


class ProgressModal(ctk.CTkToplevel):
    """Modal de progression élégante"""
    
    def __init__(self, master, total: int):
        super().__init__(master)
        
        self.title("")
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        self.total = total
        self.cancelled = False
        
        # Centrer
        self.transient(master)
        self.grab_set()
        
        # Contenu
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Icône animée (simulée)
        self.icon_label = ctk.CTkLabel(
            content,
            text="⚡",
            font=ctk.CTkFont(size=48)
        )
        self.icon_label.pack(pady=(0, 20))
        
        # Titre
        self.title_label = ctk.CTkLabel(
            content,
            text=f"Conversion de {total} fichier{'s' if total > 1 else ''}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.title_label.pack()
        
        # Fichier en cours
        self.file_label = ctk.CTkLabel(
            content,
            text="Préparation...",
            font=ctk.CTkFont(size=13),
            text_color=Theme.TEXT_SECONDARY
        )
        self.file_label.pack(pady=(8, 20))
        
        # Barre de progression
        self.progress = ctk.CTkProgressBar(
            content,
            width=360,
            height=8,
            corner_radius=4,
            fg_color=Theme.BG_TERTIARY,
            progress_color=Theme.ACCENT
        )
        self.progress.pack()
        self.progress.set(0)
        
        # Pourcentage
        self.percent_label = ctk.CTkLabel(
            content,
            text="0%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.ACCENT
        )
        self.percent_label.pack(pady=10)
        
        # Bouton annuler
        self.cancel_btn = ctk.CTkButton(
            content,
            text="Annuler",
            width=120,
            height=36,
            corner_radius=18,
            fg_color="transparent",
            hover_color=Theme.BG_TERTIARY,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._cancel
        )
        self.cancel_btn.pack(pady=(20, 0))
    
    def update_progress(self, current: int, filename: str):
        progress = current / self.total
        self.progress.set(progress)
        self.percent_label.configure(text=f"{int(progress * 100)}%")
        self.file_label.configure(text=filename[:40] + ("..." if len(filename) > 40 else ""))
        self.update()
    
    def _cancel(self):
        self.cancelled = True
        self.cancel_btn.configure(text="Annulation...", state="disabled")
    
    def complete(self, success: int, errors: int):
        self.progress.set(1)
        self.percent_label.configure(text="100%")
        
        if errors == 0:
            self.icon_label.configure(text="✅")
            self.title_label.configure(text="Conversion réussie !")
            self.file_label.configure(text=f"{success} fichier{'s' if success > 1 else ''} converti{'s' if success > 1 else ''}")
        else:
            self.icon_label.configure(text="⚠️")
            self.title_label.configure(text="Conversion terminée")
            self.file_label.configure(text=f"{success} réussi{'s' if success > 1 else ''}, {errors} erreur{'s' if errors > 1 else ''}")
        
        self.cancel_btn.configure(
            text="Fermer",
            state="normal",
            fg_color=Theme.ACCENT,
            text_color="#FFFFFF",
            border_width=0,
            command=self.destroy
        )
        
        # Notification
        self._notify(success, errors)
    
    def _notify(self, success: int, errors: int):
        try:
            msg = f"✅ {success} converti{'s' if success > 1 else ''}"
            if errors:
                msg += f", ❌ {errors} erreur{'s' if errors > 1 else ''}"
            subprocess.run([
                "osascript", "-e",
                f'display notification "{msg}" with title "Format Converter"'
            ], capture_output=True)
        except:
            pass


class FormatConverterApp(ctk.CTk):
    """Application principale avec design épuré"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Format Converter")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        # État
        self.files: List[str] = []
        self.selected_format = ctk.StringVar(value="pdf")
        self.output_folder = Path.home() / "Downloads"
        self.file_items: Dict[str, FileItem] = {}
        self.selected_file: Optional[str] = None
        
        # Raccourcis
        self.bind("<Command-o>", lambda e: self._browse())
        self.bind("<Command-Return>", lambda e: self._convert())
        self.bind("<BackSpace>", lambda e: self._clear())
        
        # Interface
        self._create_layout()
    
    def _create_layout(self):
        """Créer le layout principal"""
        # Container principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar()
        
        # Zone principale
        self._create_main()
        
        # Panneau droit
        self._create_right_panel()
    
    def _create_sidebar(self):
        """Sidebar avec formats"""
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=0,
            border_width=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo/Titre
        header = ctk.CTkFrame(sidebar, fg_color="transparent", height=80)
        header.pack(fill="x", padx=20, pady=(24, 16))
        
        ctk.CTkLabel(
            header,
            text="Format Converter",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Convertissez vos fichiers",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(4, 0))
        
        # Séparateur
        ctk.CTkFrame(sidebar, fg_color=Theme.BORDER, height=1).pack(fill="x", padx=20, pady=(0, 16))
        
        # Formats
        scroll = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_button_color=Theme.BORDER,
            scrollbar_button_hover_color=Theme.TEXT_TERTIARY
        )
        scroll.pack(fill="both", expand=True, padx=12)
        
        formats = [
            ("Documents", [
                ("PDF", "pdf", ""),
                ("Word", "docx", ""),
                ("Texte", "txt", ""),
                ("HTML", "html", ""),
            ]),
            ("Images", [
                ("PNG", "png", ""),
                ("JPEG", "jpg", ""),
                ("HEIC", "heic", ""),
                ("WebP", "webp", ""),
            ]),
            ("Audio", [
                ("MP3", "mp3", ""),
                ("WAV", "wav", ""),
                ("AAC", "aac", ""),
                ("FLAC", "flac", ""),
            ]),
            ("Vidéo", [
                ("MP4", "mp4", ""),
                ("MOV", "mov", ""),
                ("MKV", "mkv", ""),
            ]),
            ("Archives", [
                ("ZIP", "zip", ""),
                ("Extraire", "unzip", ""),
            ]),
        ]
        
        for category, items in formats:
            # Header catégorie
            ctk.CTkLabel(
                scroll,
                text=category.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=Theme.TEXT_TERTIARY
            ).pack(anchor="w", padx=8, pady=(16, 6))
            
            for name, value, icon in items:
                SidebarButton(
                    scroll,
                    text=name,
                    value=value,
                    variable=self.selected_format,
                    icon=icon
                ).pack(fill="x", pady=1)
        
        # Footer - Dossier de sortie
        footer = ctk.CTkFrame(sidebar, fg_color="transparent", height=70)
        footer.pack(fill="x", side="bottom", padx=20, pady=16)
        
        ctk.CTkLabel(
            footer,
            text="DOSSIER DE SORTIE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Theme.TEXT_TERTIARY
        ).pack(anchor="w")
        
        folder_row = ctk.CTkFrame(footer, fg_color="transparent")
        folder_row.pack(fill="x", pady=(6, 0))
        
        self.folder_label = ctk.CTkLabel(
            folder_row,
            text="📁 Downloads",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_PRIMARY
        )
        self.folder_label.pack(side="left")
        
        ctk.CTkButton(
            folder_row,
            text="Modifier",
            width=80,
            height=32,
            corner_radius=16,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=Theme.BG_TERTIARY,
            text_color=Theme.ACCENT,
            border_width=1,
            border_color=Theme.ACCENT,
            command=self._change_folder
        ).pack(side="right")
    
    def _create_main(self):
        """Zone principale"""
        main = ctk.CTkFrame(self, fg_color=Theme.BG_PRIMARY, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        
        # Container
        container = ctk.CTkFrame(main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=32, pady=28)
        
        # Drop zone
        self.drop_zone = ctk.CTkFrame(
            container,
            fg_color=Theme.BG_TERTIARY,
            corner_radius=20,
            height=180,
            border_width=2,
            border_color=Theme.BORDER
        )
        self.drop_zone.pack(fill="x")
        self.drop_zone.pack_propagate(False)
        
        drop_inner = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        drop_inner.pack(expand=True)
        
        ctk.CTkLabel(
            drop_inner,
            text="📂",
            font=ctk.CTkFont(size=48)
        ).pack()
        
        ctk.CTkLabel(
            drop_inner,
            text="Déposez vos fichiers ici",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(12, 6))
        
        ctk.CTkLabel(
            drop_inner,
            text="ou utilisez le bouton ci-dessous",
            font=ctk.CTkFont(size=13),
            text_color=Theme.TEXT_SECONDARY
        ).pack()
        
        ctk.CTkButton(
            drop_inner,
            text="Parcourir les fichiers",
            width=160,
            height=42,
            corner_radius=21,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            command=self._browse
        ).pack(pady=(16, 0))
        
        # Bind click zone
        for w in [self.drop_zone, drop_inner]:
            w.bind("<Button-1>", lambda e: self._browse())
        
        # Header fichiers
        files_header = ctk.CTkFrame(container, fg_color="transparent", height=50)
        files_header.pack(fill="x", pady=(24, 12))
        
        ctk.CTkLabel(
            files_header,
            text="Fichiers",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.count_label = ctk.CTkLabel(
            files_header,
            text="0",
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT_SECONDARY
        )
        self.count_label.pack(side="left", padx=(10, 0))
        
        ctk.CTkButton(
            files_header,
            text="Tout effacer",
            width=110,
            height=34,
            corner_radius=17,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=("#FFEBEE", "#3D1F1F"),
            text_color=Theme.DANGER,
            border_width=1,
            border_color=Theme.DANGER,
            command=self._clear
        ).pack(side="right")
        
        # Liste fichiers
        self.files_list = ctk.CTkScrollableFrame(
            container,
            fg_color=Theme.BG_TERTIARY,
            corner_radius=16,
            scrollbar_button_color=Theme.BORDER
        )
        self.files_list.pack(fill="both", expand=True, pady=(0, 4))
        
        self.empty_label = ctk.CTkLabel(
            self.files_list,
            text="Aucun fichier sélectionné",
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT_TERTIARY
        )
        self.empty_label.pack(expand=True, pady=70)
        
        # Bouton convertir
        self.convert_btn = ctk.CTkButton(
            container,
            text="✨  Convertir les fichiers",
            height=56,
            corner_radius=14,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            command=self._convert
        )
        self.convert_btn.pack(fill="x", pady=(20, 0))
    
    def _create_right_panel(self):
        """Panneau droit"""
        panel = ctk.CTkFrame(
            self,
            width=260,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=0
        )
        panel.grid(row=0, column=2, sticky="nsew")
        panel.grid_propagate(False)
        
        # Prévisualisation
        self.preview = PreviewCard(panel, fg_color="transparent")
        self.preview.pack(fill="x", padx=16, pady=(20, 12))
        
        # Options
        self.options = OptionsCard(panel, fg_color="transparent")
        self.options.pack(fill="x", padx=16, pady=12)
        
        # Actions rapides
        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(
            actions,
            text="ACTIONS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Theme.TEXT_TERTIARY
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkButton(
            actions,
            text="📋  Historique",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            command=self._show_history
        ).pack(fill="x", pady=4)
        
        ctk.CTkButton(
            actions,
            text="🔊  Extraire audio",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            command=self._extract_audio
        ).pack(fill="x", pady=4)
    
    # === ACTIONS ===
    
    def _browse(self):
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers",
            filetypes=[
                ("Tous", "*.*"),
                ("Documents", "*.pdf *.docx *.txt *.html *.md"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.webp *.heic"),
                ("Audio", "*.mp3 *.wav *.aac *.flac *.m4a"),
                ("Vidéo", "*.mp4 *.mov *.avi *.mkv"),
            ]
        )
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self._add_file(f)
        
        self._update_count()
    
    def _add_file(self, filepath: str):
        self.empty_label.pack_forget()
        
        item = FileItem(
            self.files_list,
            filepath=filepath,
            on_remove=self._remove_file,
            on_select=self._select_file
        )
        item.pack(fill="x", pady=3, padx=6)
        self.file_items[filepath] = item
    
    def _remove_file(self, filepath: str):
        if filepath in self.files:
            self.files.remove(filepath)
        if filepath in self.file_items:
            self.file_items[filepath].destroy()
            del self.file_items[filepath]
        
        if filepath == self.selected_file:
            self.selected_file = None
            self.preview.clear()
        
        self._update_count()
        
        if not self.files:
            self.empty_label.pack(expand=True, pady=60)
    
    def _select_file(self, filepath: str):
        # Désélectionner l'ancien
        if self.selected_file and self.selected_file in self.file_items:
            self.file_items[self.selected_file].set_selected(False)
        
        # Sélectionner le nouveau
        self.selected_file = filepath
        if filepath in self.file_items:
            self.file_items[filepath].set_selected(True)
        
        self.preview.show(filepath)
    
    def _clear(self):
        for item in self.file_items.values():
            item.destroy()
        self.files.clear()
        self.file_items.clear()
        self.selected_file = None
        self.preview.clear()
        self._update_count()
        self.empty_label.pack(expand=True, pady=60)
    
    def _update_count(self):
        n = len(self.files)
        self.count_label.configure(text=str(n))
    
    def _change_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = Path(folder)
            self.folder_label.configure(text=f"📁 {self.output_folder.name}")
    
    def _convert(self):
        if not self.files:
            return
        
        modal = ProgressModal(self, len(self.files))
        opts = self.options.get_options()
        fmt = self.selected_format.get()
        
        thread = threading.Thread(target=self._do_convert, args=(fmt, opts, modal))
        thread.start()
    
    def _do_convert(self, fmt: str, opts: ConversionOptions, modal: ProgressModal):
        success = errors = 0
        
        for i, filepath in enumerate(self.files):
            if modal.cancelled:
                break
            
            name = Path(filepath).name
            self.after(0, lambda idx=i+1, n=name: modal.update_progress(idx, n))
            
            try:
                self._convert_file(filepath, fmt, opts)
                ConversionHistory.add(filepath, "", fmt, True)
                success += 1
            except Exception as e:
                ConversionHistory.add(filepath, "", fmt, False)
                errors += 1
        
        self.after(0, lambda: modal.complete(success, errors))
        self.after(0, self._clear)
    
    def _convert_file(self, input_path: str, fmt: str, opts: ConversionOptions):
        """Convertir un fichier"""
        path = Path(input_path)
        ext = path.suffix.lower()[1:]
        output = self.output_folder / f"{path.stem}.{fmt}"
        
        # Éviter conflits
        c = 1
        while output.exists():
            output = self.output_folder / f"{path.stem} ({c}).{fmt}"
            c += 1
        
        # Images
        if fmt in ["png", "jpg", "jpeg", "gif", "tiff", "webp", "heic"]:
            img = Image.open(input_path)
            
            if opts.resize_width and opts.resize_height:
                img = img.resize((opts.resize_width, opts.resize_height), Image.Resampling.LANCZOS)
            
            if fmt in ["jpg", "jpeg"] and img.mode in ["RGBA", "P"]:
                img = img.convert("RGB")
            
            if fmt == "heic":
                subprocess.run(["sips", "-s", "format", "heic", input_path, "--out", str(output)],
                             check=True, capture_output=True)
            elif fmt in ["jpg", "jpeg"]:
                img.save(str(output), quality=opts.quality)
            else:
                img.save(str(output))
        
        # Image → PDF
        elif fmt == "pdf" and ext in ["png", "jpg", "jpeg", "gif", "tiff", "webp"]:
            img = Image.open(input_path)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(str(output), "PDF", resolution=100.0)
        
        # Audio
        elif fmt in ["mp3", "wav", "aac", "flac", "m4a"]:
            cmd = ["ffmpeg", "-i", input_path, "-y"]
            if fmt == "mp3":
                cmd += ["-codec:a", "libmp3lame", "-b:a", opts.bitrate_audio]
            elif fmt == "wav":
                cmd += ["-codec:a", "pcm_s16le"]
            elif fmt in ["aac", "m4a"]:
                cmd += ["-codec:a", "aac", "-b:a", opts.bitrate_audio]
            elif fmt == "flac":
                cmd += ["-codec:a", "flac"]
            cmd.append(str(output))
            subprocess.run(cmd, check=True, capture_output=True)
        
        # Vidéo
        elif fmt in ["mp4", "mov", "mkv"]:
            cmd = ["ffmpeg", "-i", input_path, "-y"]
            if fmt == "mp4":
                cmd += ["-codec:v", "libx264", "-preset", "medium", "-crf", "23",
                       "-codec:a", "aac", "-b:a", "128k"]
            else:
                cmd += ["-codec:v", "copy", "-codec:a", "copy"]
            cmd.append(str(output))
            subprocess.run(cmd, check=True, capture_output=True)
        
        # Archives
        elif fmt == "zip":
            subprocess.run(["zip", "-r", str(output), path.name],
                         cwd=str(path.parent), check=True, capture_output=True)
        elif fmt == "unzip":
            out_dir = self.output_folder / path.stem
            out_dir.mkdir(exist_ok=True)
            if ext == "zip":
                subprocess.run(["unzip", "-o", input_path, "-d", str(out_dir)],
                             check=True, capture_output=True)
            elif ext in ["tar", "gz"]:
                subprocess.run(["tar", "-xf", input_path, "-C", str(out_dir)],
                             check=True, capture_output=True)
            elif ext == "7z":
                subprocess.run(["7z", "x", input_path, f"-o{out_dir}"],
                             check=True, capture_output=True)
        
        # Documents
        elif fmt in ["pdf", "docx", "txt", "html"]:
            soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            if os.path.exists(soffice):
                subprocess.run([
                    soffice, "--headless", "--convert-to", fmt,
                    "--outdir", str(self.output_folder), input_path
                ], check=True, capture_output=True)
            elif shutil.which("pandoc"):
                subprocess.run(["pandoc", input_path, "-o", str(output)],
                             check=True, capture_output=True)
    
    def _show_history(self):
        """Afficher l'historique"""
        win = ctk.CTkToplevel(self)
        win.title("Historique")
        win.geometry("500x400")
        win.configure(fg_color=Theme.BG_PRIMARY)
        
        history = ConversionHistory.load()
        
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        if not history:
            ctk.CTkLabel(scroll, text="Aucun historique", text_color=Theme.TEXT_SECONDARY).pack(pady=50)
            return
        
        for item in reversed(history[-20:]):
            row = ctk.CTkFrame(scroll, fg_color=Theme.BG_CARD, corner_radius=8, height=50)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=8)
            
            status = "✅" if item.get("success") else "❌"
            ctk.CTkLabel(inner, text=status, width=24).pack(side="left")
            
            name = Path(item.get("input", "")).name[:30]
            ctk.CTkLabel(inner, text=name, font=ctk.CTkFont(size=12)).pack(side="left", padx=8)
            
            fmt = item.get("format", "").upper()
            ctk.CTkLabel(inner, text=f"→ {fmt}", text_color=Theme.TEXT_SECONDARY).pack(side="right")
    
    def _extract_audio(self):
        """Extraire audio d'une vidéo"""
        video = filedialog.askopenfilename(filetypes=[("Vidéo", "*.mp4 *.mov *.avi *.mkv")])
        if not video:
            return
        
        output = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav")]
        )
        if not output:
            return
        
        try:
            subprocess.run([
                "ffmpeg", "-i", video, "-vn", "-codec:a", "libmp3lame", "-q:a", "2", "-y", output
            ], check=True, capture_output=True)
            messagebox.showinfo("Succès", f"Audio extrait:\n{output}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


def main():
    app = FormatConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
