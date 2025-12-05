#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format Converter 2.0 - Application complète
Toutes les fonctionnalités de conversion avec interface moderne
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import os
import sys
import shutil
import json
from pathlib import Path
from PIL import Image, ImageTk
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable
import platform

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Chemin de l'historique
HISTORY_FILE = Path.home() / ".format_converter_history.json"


class ConversionOptions:
    """Options de conversion"""
    def __init__(self):
        self.quality: int = 85  # 1-100
        self.resize_width: Optional[int] = None
        self.resize_height: Optional[int] = None
        self.keep_aspect_ratio: bool = True
        self.bitrate_audio: str = "256k"
        self.bitrate_video: str = "5M"
        self.resolution: str = "original"  # 1080p, 720p, 480p, original
        self.compression_level: int = 6  # 1-9
        self.password: Optional[str] = None
        self.prefix: str = ""
        self.suffix: str = ""


class ConversionHistory:
    """Gestionnaire d'historique"""
    
    @staticmethod
    def load() -> List[Dict]:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    @staticmethod
    def save(history: List[Dict]):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history[-100:], f, indent=2, default=str)  # Garder les 100 derniers
    
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


class PreviewPanel(ctk.CTkFrame):
    """Panneau de prévisualisation"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=12)
        
        # Titre
        self.title = ctk.CTkLabel(
            self,
            text="Prévisualisation",
            font=ctk.CTkFont(family="SF Pro Display", size=14, weight="bold"),
            text_color=("#1d1d1f", "#f5f5f7")
        )
        self.title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Zone de prévisualisation
        self.preview_frame = ctk.CTkFrame(self, fg_color=("#e5e5e7", "#2c2c2e"), corner_radius=8)
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Image/Contenu
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Sélectionnez un fichier\npour voir l'aperçu",
            font=ctk.CTkFont(size=12),
            text_color=("#86868b", "#98989f")
        )
        self.preview_label.pack(expand=True, pady=20)
        
        # Info fichier
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#86868b", "#98989f")
        )
        self.info_label.pack(pady=(0, 10), padx=15)
        
        self.current_image = None
    
    def show_preview(self, filepath: str):
        """Afficher la prévisualisation d'un fichier"""
        path = Path(filepath)
        ext = path.suffix.lower()
        
        # Info fichier
        try:
            size = path.stat().st_size
            size_str = self._format_size(size)
            self.info_label.configure(text=f"{path.name}\n{size_str}")
        except:
            self.info_label.configure(text=path.name)
        
        # Prévisualisation selon le type
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.heic']:
            self._show_image(filepath)
        elif ext in ['.txt', '.md', '.json', '.xml', '.csv', '.yaml', '.yml', '.html']:
            self._show_text(filepath)
        elif ext == '.pdf':
            self._show_pdf_info(filepath)
        elif ext in ['.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg']:
            self._show_audio_info(filepath)
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            self._show_video_info(filepath)
        else:
            self._show_generic(filepath)
    
    def _show_image(self, filepath: str):
        """Afficher une image"""
        try:
            img = Image.open(filepath)
            # Redimensionner pour l'aperçu
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            self.current_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.preview_label.configure(image=self.current_image, text="")
            
            # Ajouter les dimensions
            orig_img = Image.open(filepath)
            self.info_label.configure(
                text=f"{Path(filepath).name}\n{orig_img.width} × {orig_img.height} px"
            )
        except Exception as e:
            self.preview_label.configure(image=None, text=f"Erreur: {e}")
    
    def _show_text(self, filepath: str):
        """Afficher un aperçu texte"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)
                if len(content) == 500:
                    content += "..."
            self.preview_label.configure(image=None, text=content[:200])
        except:
            self.preview_label.configure(image=None, text="Impossible de lire le fichier")
    
    def _show_pdf_info(self, filepath: str):
        """Afficher info PDF"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            pages = len(reader.pages)
            self.preview_label.configure(image=None, text=f"📄 PDF\n{pages} page(s)")
        except:
            self.preview_label.configure(image=None, text="📄 PDF")
    
    def _show_audio_info(self, filepath: str):
        """Afficher info audio"""
        self.preview_label.configure(image=None, text="🎵 Fichier audio")
    
    def _show_video_info(self, filepath: str):
        """Afficher info vidéo"""
        self.preview_label.configure(image=None, text="🎬 Fichier vidéo")
    
    def _show_generic(self, filepath: str):
        """Afficher info générique"""
        ext = Path(filepath).suffix.upper()
        self.preview_label.configure(image=None, text=f"📄 Fichier {ext}")
    
    def clear(self):
        """Effacer la prévisualisation"""
        self.preview_label.configure(image=None, text="Sélectionnez un fichier\npour voir l'aperçu")
        self.info_label.configure(text="")
        self.current_image = None
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} To"


class OptionsPanel(ctk.CTkFrame):
    """Panneau d'options de conversion"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=12)
        self.options = ConversionOptions()
        
        # Titre
        ctk.CTkLabel(
            self,
            text="⚙️ Options",
            font=ctk.CTkFont(family="SF Pro Display", size=14, weight="bold")
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Qualité (images)
        self.quality_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quality_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.quality_frame,
            text="Qualité:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="85%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#007aff", "#0a84ff")
        )
        self.quality_label.pack(side="right")
        
        self.quality_slider = ctk.CTkSlider(
            self,
            from_=10,
            to=100,
            number_of_steps=90,
            command=self._on_quality_change
        )
        self.quality_slider.set(85)
        self.quality_slider.pack(fill="x", padx=15, pady=(0, 10))
        
        # Redimensionner
        self.resize_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.resize_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.resize_frame,
            text="Redimensionner:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.resize_var = ctk.StringVar(value="original")
        self.resize_menu = ctk.CTkOptionMenu(
            self.resize_frame,
            values=["Original", "1920×1080", "1280×720", "800×600", "Personnalisé"],
            variable=self.resize_var,
            command=self._on_resize_change,
            width=120,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.resize_menu.pack(side="right")
        
        # Dimensions personnalisées
        self.custom_size_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.width_entry = ctk.CTkEntry(
            self.custom_size_frame,
            placeholder_text="Largeur",
            width=70,
            height=28
        )
        self.width_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(self.custom_size_frame, text="×").pack(side="left")
        
        self.height_entry = ctk.CTkEntry(
            self.custom_size_frame,
            placeholder_text="Hauteur",
            width=70,
            height=28
        )
        self.height_entry.pack(side="left", padx=(5, 0))
        
        # Bitrate audio
        self.bitrate_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bitrate_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.bitrate_frame,
            text="Bitrate audio:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.bitrate_var = ctk.StringVar(value="256k")
        self.bitrate_menu = ctk.CTkOptionMenu(
            self.bitrate_frame,
            values=["128k", "192k", "256k", "320k"],
            variable=self.bitrate_var,
            width=80,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.bitrate_menu.pack(side="right")
        
        # Préfixe/Suffixe
        self.naming_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.naming_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.naming_frame,
            text="Préfixe:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.prefix_entry = ctk.CTkEntry(
            self.naming_frame,
            placeholder_text="ex: converted_",
            width=100,
            height=28
        )
        self.prefix_entry.pack(side="right")
        
        # Conserver le ratio
        self.ratio_var = ctk.BooleanVar(value=True)
        self.ratio_check = ctk.CTkCheckBox(
            self,
            text="Conserver les proportions",
            variable=self.ratio_var,
            font=ctk.CTkFont(size=12)
        )
        self.ratio_check.pack(padx=15, pady=10, anchor="w")
    
    def _on_quality_change(self, value):
        self.options.quality = int(value)
        self.quality_label.configure(text=f"{int(value)}%")
    
    def _on_resize_change(self, value):
        if value == "Personnalisé":
            self.custom_size_frame.pack(fill="x", padx=15, pady=5)
        else:
            self.custom_size_frame.pack_forget()
            
            if value == "Original":
                self.options.resize_width = None
                self.options.resize_height = None
            elif "×" in value:
                w, h = value.split("×")
                self.options.resize_width = int(w)
                self.options.resize_height = int(h)
    
    def get_options(self) -> ConversionOptions:
        """Récupérer les options actuelles"""
        self.options.quality = int(self.quality_slider.get())
        self.options.bitrate_audio = self.bitrate_var.get()
        self.options.keep_aspect_ratio = self.ratio_var.get()
        self.options.prefix = self.prefix_entry.get()
        
        # Dimensions personnalisées
        if self.resize_var.get() == "Personnalisé":
            try:
                self.options.resize_width = int(self.width_entry.get())
                self.options.resize_height = int(self.height_entry.get())
            except:
                pass
        
        return self.options


class ProgressWindow(ctk.CTkToplevel):
    """Fenêtre de progression détaillée"""
    
    def __init__(self, master, total_files: int):
        super().__init__(master)
        self.title("Conversion en cours...")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.total = total_files
        self.current = 0
        self.cancelled = False
        
        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text=f"Conversion de {total_files} fichier(s)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # Progression globale
        ctk.CTkLabel(self, text="Progression globale:").pack(anchor="w", padx=20)
        self.global_progress = ctk.CTkProgressBar(self, width=460)
        self.global_progress.pack(padx=20, pady=(5, 15))
        self.global_progress.set(0)
        
        self.global_label = ctk.CTkLabel(self, text="0%")
        self.global_label.pack()
        
        # Fichier en cours
        ctk.CTkLabel(self, text="Fichier en cours:").pack(anchor="w", padx=20, pady=(15, 5))
        self.current_file_label = ctk.CTkLabel(
            self,
            text="En attente...",
            font=ctk.CTkFont(size=12),
            text_color=("#86868b", "#98989f")
        )
        self.current_file_label.pack(anchor="w", padx=20)
        
        self.file_progress = ctk.CTkProgressBar(self, width=460)
        self.file_progress.pack(padx=20, pady=10)
        self.file_progress.set(0)
        
        # Log
        self.log_frame = ctk.CTkScrollableFrame(self, height=120)
        self.log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bouton annuler
        self.cancel_btn = ctk.CTkButton(
            self,
            text="Annuler",
            fg_color=("#ff3b30", "#ff453a"),
            hover_color=("#d63030", "#d63030"),
            command=self.cancel
        )
        self.cancel_btn.pack(pady=15)
        
        self.grab_set()
    
    def update_progress(self, current: int, filename: str, status: str = ""):
        """Mettre à jour la progression"""
        self.current = current
        progress = current / self.total if self.total > 0 else 0
        
        self.global_progress.set(progress)
        self.global_label.configure(text=f"{int(progress * 100)}%")
        self.current_file_label.configure(text=filename)
        self.file_progress.set(0)
        
        # Ajouter au log
        self.add_log(f"{'✅' if 'success' in status.lower() else '🔄'} {filename}")
        
        self.update()
    
    def add_log(self, message: str):
        """Ajouter un message au log"""
        label = ctk.CTkLabel(
            self.log_frame,
            text=message,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        label.pack(anchor="w", pady=1)
    
    def cancel(self):
        """Annuler la conversion"""
        self.cancelled = True
        self.cancel_btn.configure(text="Annulation...", state="disabled")
    
    def complete(self, success: int, errors: int):
        """Conversion terminée"""
        self.global_progress.set(1)
        self.global_label.configure(text="100%")
        self.title_label.configure(text="Conversion terminée !")
        self.cancel_btn.configure(text="Fermer", state="normal", 
                                  fg_color=("#007aff", "#0a84ff"),
                                  command=self.destroy)
        
        # Notification système
        self._send_notification(success, errors)
    
    def _send_notification(self, success: int, errors: int):
        """Envoyer une notification macOS"""
        try:
            title = "Format Converter"
            message = f"✅ {success} fichier(s) converti(s)"
            if errors > 0:
                message += f"\n❌ {errors} erreur(s)"
            
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], capture_output=True)
        except:
            pass


class HistoryWindow(ctk.CTkToplevel):
    """Fenêtre d'historique"""
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Historique des conversions")
        self.geometry("700x500")
        
        # Titre
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📋 Historique",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="Effacer",
            fg_color=("#ff3b30", "#ff453a"),
            width=80,
            command=self._clear_history
        ).pack(side="right")
        
        # Liste
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._load_history()
    
    def _load_history(self):
        """Charger l'historique"""
        history = ConversionHistory.load()
        
        if not history:
            ctk.CTkLabel(
                self.list_frame,
                text="Aucune conversion dans l'historique",
                text_color=("#86868b", "#98989f")
            ).pack(pady=50)
            return
        
        for item in reversed(history):
            self._add_history_item(item)
    
    def _add_history_item(self, item: Dict):
        """Ajouter un élément à l'historique"""
        frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2c2c2e"), corner_radius=8)
        frame.pack(fill="x", pady=3)
        
        # Status
        status = "✅" if item.get("success", False) else "❌"
        ctk.CTkLabel(frame, text=status, width=30).pack(side="left", padx=10)
        
        # Info
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=8)
        
        ctk.CTkLabel(
            info_frame,
            text=Path(item.get("input", "")).name,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"→ {item.get('format', '').upper()} | {item.get('timestamp', '')[:16]}",
            font=ctk.CTkFont(size=10),
            text_color=("#86868b", "#98989f"),
            anchor="w"
        ).pack(anchor="w")
    
    def _clear_history(self):
        """Effacer l'historique"""
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self.list_frame,
            text="Historique effacé",
            text_color=("#86868b", "#98989f")
        ).pack(pady=50)


class PDFToolsWindow(ctk.CTkToplevel):
    """Fenêtre d'outils PDF"""
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Outils PDF")
        self.geometry("500x400")
        
        self.files: List[str] = []
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tab Fusionner
        self.merge_tab = self.tabview.add("Fusionner")
        self._create_merge_tab()
        
        # Tab Diviser
        self.split_tab = self.tabview.add("Diviser")
        self._create_split_tab()
        
        # Tab Compresser
        self.compress_tab = self.tabview.add("Compresser")
        self._create_compress_tab()
    
    def _create_merge_tab(self):
        """Créer l'onglet fusion"""
        ctk.CTkLabel(
            self.merge_tab,
            text="Fusionner plusieurs PDF en un seul",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        self.merge_list = ctk.CTkScrollableFrame(self.merge_tab, height=150)
        self.merge_list.pack(fill="x", pady=10)
        
        btn_frame = ctk.CTkFrame(self.merge_tab, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Ajouter des PDF",
            command=self._add_pdfs
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Fusionner",
            fg_color=("#34c759", "#30d158"),
            command=self._merge_pdfs
        ).pack(side="right", padx=5)
    
    def _create_split_tab(self):
        """Créer l'onglet division"""
        ctk.CTkLabel(
            self.split_tab,
            text="Diviser un PDF en plusieurs fichiers",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        self.split_file_label = ctk.CTkLabel(
            self.split_tab,
            text="Aucun fichier sélectionné",
            text_color=("#86868b", "#98989f")
        )
        self.split_file_label.pack(pady=10)
        
        ctk.CTkButton(
            self.split_tab,
            text="Sélectionner un PDF",
            command=self._select_pdf_to_split
        ).pack(pady=5)
        
        # Options
        options_frame = ctk.CTkFrame(self.split_tab, fg_color="transparent")
        options_frame.pack(pady=15)
        
        ctk.CTkLabel(options_frame, text="Pages par fichier:").pack(side="left")
        self.pages_per_file = ctk.CTkEntry(options_frame, width=60, placeholder_text="1")
        self.pages_per_file.pack(side="left", padx=10)
        
        ctk.CTkButton(
            self.split_tab,
            text="Diviser",
            fg_color=("#34c759", "#30d158"),
            command=self._split_pdf
        ).pack(pady=10)
    
    def _create_compress_tab(self):
        """Créer l'onglet compression"""
        ctk.CTkLabel(
            self.compress_tab,
            text="Compresser un PDF",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        self.compress_file_label = ctk.CTkLabel(
            self.compress_tab,
            text="Aucun fichier sélectionné",
            text_color=("#86868b", "#98989f")
        )
        self.compress_file_label.pack(pady=10)
        
        ctk.CTkButton(
            self.compress_tab,
            text="Sélectionner un PDF",
            command=self._select_pdf_to_compress
        ).pack(pady=5)
        
        # Qualité
        quality_frame = ctk.CTkFrame(self.compress_tab, fg_color="transparent")
        quality_frame.pack(pady=15)
        
        ctk.CTkLabel(quality_frame, text="Qualité:").pack(side="left")
        self.compress_quality = ctk.CTkOptionMenu(
            quality_frame,
            values=["Haute", "Moyenne", "Basse"]
        )
        self.compress_quality.pack(side="left", padx=10)
        
        ctk.CTkButton(
            self.compress_tab,
            text="Compresser",
            fg_color=("#34c759", "#30d158"),
            command=self._compress_pdf
        ).pack(pady=10)
    
    def _add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for f in files:
            self.files.append(f)
            ctk.CTkLabel(self.merge_list, text=Path(f).name).pack(anchor="w")
    
    def _merge_pdfs(self):
        if len(self.files) < 2:
            messagebox.showwarning("Attention", "Sélectionnez au moins 2 PDF")
            return
        
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not output:
            return
        
        try:
            from pypdf import PdfMerger
            merger = PdfMerger()
            for pdf in self.files:
                merger.append(pdf)
            merger.write(output)
            merger.close()
            messagebox.showinfo("Succès", f"PDF fusionné: {output}")
        except ImportError:
            messagebox.showerror("Erreur", "pypdf requis: pip install pypdf")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def _select_pdf_to_split(self):
        self.split_file = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if self.split_file:
            self.split_file_label.configure(text=Path(self.split_file).name)
    
    def _split_pdf(self):
        if not hasattr(self, 'split_file') or not self.split_file:
            return
        
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
        
        try:
            from pypdf import PdfReader, PdfWriter
            reader = PdfReader(self.split_file)
            pages_per = int(self.pages_per_file.get() or 1)
            
            for i in range(0, len(reader.pages), pages_per):
                writer = PdfWriter()
                for j in range(i, min(i + pages_per, len(reader.pages))):
                    writer.add_page(reader.pages[j])
                
                output_path = Path(output_dir) / f"page_{i+1}-{min(i+pages_per, len(reader.pages))}.pdf"
                with open(output_path, 'wb') as f:
                    writer.write(f)
            
            messagebox.showinfo("Succès", f"PDF divisé dans {output_dir}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def _select_pdf_to_compress(self):
        self.compress_file = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if self.compress_file:
            self.compress_file_label.configure(text=Path(self.compress_file).name)
    
    def _compress_pdf(self):
        if not hasattr(self, 'compress_file') or not self.compress_file:
            return
        
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not output:
            return
        
        try:
            # Utiliser Ghostscript si disponible
            gs = "/opt/homebrew/bin/gs" if os.path.exists("/opt/homebrew/bin/gs") else "gs"
            quality_map = {"Haute": "/prepress", "Moyenne": "/ebook", "Basse": "/screen"}
            quality = quality_map.get(self.compress_quality.get(), "/ebook")
            
            subprocess.run([
                gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={quality}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
                f"-sOutputFile={output}", self.compress_file
            ], check=True)
            
            messagebox.showinfo("Succès", f"PDF compressé: {output}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Ghostscript requis: brew install ghostscript\n{e}")


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
    """Carte de fichier"""
    
    def __init__(self, master, filepath: str, on_remove: Callable, on_select: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.filepath = filepath
        self.configure(fg_color=("#ffffff", "#2c2c2e"), corner_radius=10, height=50)
        self.pack_propagate(False)
        
        path = Path(filepath)
        
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Icône
        icon = self._get_icon(path.suffix.lower())
        ctk.CTkLabel(container, text=icon, font=ctk.CTkFont(size=20), width=30).pack(side="left")
        
        # Info
        info = ctk.CTkFrame(container, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=5)
        
        name = path.name[:35] + "..." if len(path.name) > 35 else path.name
        ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
        
        try:
            size = self._format_size(path.stat().st_size)
            ctk.CTkLabel(info, text=size, font=ctk.CTkFont(size=10), text_color=("#86868b", "#98989f")).pack(anchor="w")
        except:
            pass
        
        # Bouton supprimer
        ctk.CTkButton(
            container, text="✕", width=24, height=24, corner_radius=12,
            fg_color="transparent", hover_color=("#ff3b30", "#ff453a"),
            text_color=("#86868b", "#98989f"),
            command=lambda: on_remove(filepath)
        ).pack(side="right")
        
        # Clic pour prévisualiser
        self.bind("<Button-1>", lambda e: on_select(filepath))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: on_select(filepath))
    
    @staticmethod
    def _get_icon(ext: str) -> str:
        icons = {
            ".pdf": "📕", ".docx": "📘", ".doc": "📘", ".txt": "📝",
            ".png": "🖼️", ".jpg": "📷", ".jpeg": "📷", ".gif": "🎞️",
            ".mp3": "🎵", ".wav": "🔊", ".mp4": "🎬", ".mov": "📹",
            ".zip": "📦", ".json": "📊", ".csv": "📈"
        }
        return icons.get(ext, "📄")
    
    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"


class FormatConverterApp(ctk.CTk):
    """Application principale v2.0"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Format Converter")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Icône
        try:
            icon_path = Path(__file__).parent / "icons" / "AppIcon.png"
            if icon_path.exists():
                self.iconphoto(True, ImageTk.PhotoImage(file=str(icon_path)))
        except:
            pass
        
        # Variables
        self.files: List[str] = []
        self.selected_format = ctk.StringVar(value="pdf")
        self.output_folder = Path.home() / "Downloads"
        self.file_cards: Dict[str, FileCard] = {}
        
        # Raccourcis clavier
        self._setup_shortcuts()
        
        # Menu
        self._create_menu()
        
        # Interface
        self._create_ui()
    
    def _setup_shortcuts(self):
        """Configurer les raccourcis clavier"""
        self.bind("<Command-o>", lambda e: self.browse_files())
        self.bind("<Command-Return>", lambda e: self.start_conversion())
        self.bind("<Command-,>", lambda e: self._show_options())
        self.bind("<Command-h>", lambda e: HistoryWindow(self))
        self.bind("<Delete>", lambda e: self.clear_files())
        self.bind("<BackSpace>", lambda e: self.clear_files())
    
    def _create_menu(self):
        """Créer la barre de menu"""
        menubar = Menu(self)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Ouvrir...", accelerator="⌘O", command=self.browse_files)
        file_menu.add_command(label="Convertir", accelerator="⌘↵", command=self.start_conversion)
        file_menu.add_separator()
        file_menu.add_command(label="Historique", accelerator="⌘H", command=lambda: HistoryWindow(self))
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Outils
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Outils PDF", command=lambda: PDFToolsWindow(self))
        tools_menu.add_command(label="Extraire audio de vidéo", command=self._extract_audio)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        
        self.config(menu=menubar)
    
    def _create_ui(self):
        """Créer l'interface"""
        # Container principal avec 3 colonnes
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # === SIDEBAR GAUCHE (Formats) ===
        self._create_sidebar()
        
        # === ZONE CENTRALE ===
        self._create_main_area()
        
        # === PANNEAU DROIT (Prévisualisation + Options) ===
        self._create_right_panel()
    
    def _create_sidebar(self):
        """Créer la sidebar des formats"""
        sidebar = ctk.CTkFrame(self, width=240, fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Titre
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=70)
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            title_frame,
            text="Format Converter",
            font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="v2.0 - Convertissez tout",
            font=ctk.CTkFont(size=11),
            text_color=("#86868b", "#98989f")
        ).pack(anchor="w")
        
        # Formats
        scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=10)
        
        categories = [
            ("DOCUMENTS", [
                ("PDF", "pdf", "📕"),
                ("Word", "docx", "📘"),
                ("Texte", "txt", "📝"),
                ("HTML", "html", "🌐"),
                ("Markdown", "md", "📋"),
            ]),
            ("IMAGES", [
                ("PNG", "png", "🖼️"),
                ("JPEG", "jpg", "📷"),
                ("HEIC", "heic", "📱"),
                ("WebP", "webp", "🌅"),
                ("GIF", "gif", "🎞️"),
                ("TIFF", "tiff", "🏞️"),
            ]),
            ("AUDIO", [
                ("MP3", "mp3", "🎵"),
                ("WAV", "wav", "🔊"),
                ("AAC", "aac", "🎧"),
                ("FLAC", "flac", "💿"),
                ("M4A", "m4a", "🎶"),
            ]),
            ("VIDÉO", [
                ("MP4", "mp4", "🎬"),
                ("MOV", "mov", "📹"),
                ("AVI", "avi", "📼"),
                ("MKV", "mkv", "🎥"),
                ("WebM", "webm", "🌐"),
            ]),
            ("SPÉCIAL", [
                ("Extraire Audio", "extract_audio", "🔊"),
            ]),
            ("ARCHIVES", [
                ("ZIP", "zip", "📦"),
                ("Extraire", "unzip", "📂"),
                ("TAR", "tar", "🗃️"),
                ("7Z", "7z", "🗜️"),
            ]),
        ]
        
        for cat_name, formats in categories:
            ctk.CTkLabel(
                scroll,
                text=cat_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#86868b", "#98989f")
            ).pack(anchor="w", padx=8, pady=(12, 4))
            
            for name, value, icon in formats:
                FormatButton(scroll, text=name, value=value, variable=self.selected_format, icon=icon).pack(fill="x", pady=1, padx=4)
        
        # Footer
        footer = ctk.CTkFrame(sidebar, fg_color="transparent", height=90)
        footer.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(footer, text="📂 Sortie:", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("#86868b", "#98989f")).pack(anchor="w")
        
        self.output_label = ctk.CTkLabel(footer, text="Downloads", font=ctk.CTkFont(size=12))
        self.output_label.pack(anchor="w", pady=2)
        
        ctk.CTkButton(
            footer, text="Changer", height=28, width=80,
            fg_color="transparent", hover_color=("#e5e5e7", "#3a3a3c"),
            text_color=("#007aff", "#0a84ff"),
            command=self._change_output
        ).pack(anchor="w", pady=5)
    
    def _create_main_area(self):
        """Créer la zone centrale"""
        main = ctk.CTkFrame(self, fg_color=("#ffffff", "#000000"), corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        
        container = ctk.CTkFrame(main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Zone de drop
        drop_zone = ctk.CTkFrame(container, fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=16, height=180)
        drop_zone.pack(fill="x", pady=(0, 15))
        drop_zone.pack_propagate(False)
        
        inner = ctk.CTkFrame(drop_zone, fg_color="transparent")
        inner.pack(expand=True)
        
        ctk.CTkLabel(inner, text="📁", font=ctk.CTkFont(size=48)).pack(pady=(15, 10))
        ctk.CTkLabel(inner, text="Déposez vos fichiers ici", font=ctk.CTkFont(size=16, weight="bold")).pack()
        ctk.CTkLabel(inner, text="ou cliquez pour parcourir • ⌘O", font=ctk.CTkFont(size=12),
                     text_color=("#86868b", "#98989f")).pack(pady=5)
        
        ctk.CTkButton(
            inner, text="Parcourir", height=36, width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.browse_files
        ).pack(pady=10)
        
        # Bind click
        for widget in [drop_zone, inner]:
            widget.bind("<Button-1>", lambda e: self.browse_files())
        
        # Header fichiers
        header = ctk.CTkFrame(container, fg_color="transparent", height=40)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text="Fichiers", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        self.count_label = ctk.CTkLabel(header, text="0 fichier", font=ctk.CTkFont(size=12),
                                         text_color=("#86868b", "#98989f"))
        self.count_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            header, text="Tout effacer", height=26, width=90,
            fg_color="transparent", hover_color=("#ffeceb", "#3a2c2b"),
            text_color=("#ff3b30", "#ff453a"), font=ctk.CTkFont(size=11),
            command=self.clear_files
        ).pack(side="right")
        
        # Liste fichiers
        self.files_scroll = ctk.CTkScrollableFrame(
            container, fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=12
        )
        self.files_scroll.pack(fill="both", expand=True, pady=10)
        
        self.empty_label = ctk.CTkLabel(
            self.files_scroll,
            text="Aucun fichier • Utilisez le bouton Parcourir ou glissez-déposez",
            font=ctk.CTkFont(size=13),
            text_color=("#86868b", "#98989f")
        )
        self.empty_label.pack(expand=True, pady=40)
        
        # Bouton convertir
        self.convert_btn = ctk.CTkButton(
            container, text="🔄 Convertir • ⌘↵", height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#007aff", "#0a84ff"),
            command=self.start_conversion
        )
        self.convert_btn.pack(fill="x", pady=(10, 0))
    
    def _create_right_panel(self):
        """Créer le panneau droit"""
        right = ctk.CTkFrame(self, width=280, fg_color=("#f5f5f7", "#1c1c1e"), corner_radius=0)
        right.grid(row=0, column=2, sticky="nsew")
        right.grid_propagate(False)
        
        # Prévisualisation
        self.preview_panel = PreviewPanel(right, fg_color="transparent")
        self.preview_panel.pack(fill="x", padx=10, pady=10)
        
        # Options
        self.options_panel = OptionsPanel(right, fg_color="transparent")
        self.options_panel.pack(fill="x", padx=10, pady=5)
        
        # Boutons outils
        tools_frame = ctk.CTkFrame(right, fg_color="transparent")
        tools_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkButton(
            tools_frame, text="📄 Outils PDF", height=36,
            fg_color=("#34c759", "#30d158"),
            command=lambda: PDFToolsWindow(self)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            tools_frame, text="📋 Historique", height=36,
            fg_color=("#5856d6", "#5e5ce6"),
            command=lambda: HistoryWindow(self)
        ).pack(fill="x", pady=3)
    
    def browse_files(self):
        """Ouvrir le sélecteur de fichiers"""
        files = filedialog.askopenfilenames(
            title="Sélectionnez les fichiers à convertir",
            filetypes=[
                ("Tous", "*.*"),
                ("Documents", "*.pdf *.docx *.doc *.txt *.rtf *.html *.md"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.webp *.tiff *.bmp *.heic"),
                ("Audio", "*.mp3 *.wav *.aac *.flac *.ogg *.m4a"),
                ("Vidéo", "*.mp4 *.mov *.avi *.mkv *.webm"),
                ("Archives", "*.zip *.tar *.gz *.7z *.rar"),
            ]
        )
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self._add_file_card(f)
        
        self._update_count()
    
    def _add_file_card(self, filepath: str):
        """Ajouter une carte de fichier"""
        self.empty_label.pack_forget()
        
        card = FileCard(
            self.files_scroll,
            filepath=filepath,
            on_remove=self._remove_file,
            on_select=self._select_file
        )
        card.pack(fill="x", pady=3, padx=5)
        self.file_cards[filepath] = card
    
    def _remove_file(self, filepath: str):
        """Supprimer un fichier"""
        if filepath in self.files:
            self.files.remove(filepath)
        if filepath in self.file_cards:
            self.file_cards[filepath].destroy()
            del self.file_cards[filepath]
        
        self._update_count()
        
        if not self.files:
            self.empty_label.pack(expand=True, pady=40)
            self.preview_panel.clear()
    
    def _select_file(self, filepath: str):
        """Sélectionner un fichier pour prévisualisation"""
        self.preview_panel.show_preview(filepath)
    
    def clear_files(self):
        """Effacer tous les fichiers"""
        self.files.clear()
        for card in self.file_cards.values():
            card.destroy()
        self.file_cards.clear()
        self._update_count()
        self.empty_label.pack(expand=True, pady=40)
        self.preview_panel.clear()
    
    def _update_count(self):
        """Mettre à jour le compteur"""
        n = len(self.files)
        self.count_label.configure(text=f"{n} fichier{'s' if n > 1 else ''}")
    
    def _change_output(self):
        """Changer le dossier de sortie"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = Path(folder)
            self.output_label.configure(text=self.output_folder.name)
    
    def _show_options(self):
        """Afficher les options"""
        pass  # Les options sont déjà visibles dans le panneau droit
    
    def _extract_audio(self):
        """Extraire l'audio d'une vidéo"""
        video = filedialog.askopenfilename(filetypes=[
            ("Vidéo", "*.mp4 *.mov *.avi *.mkv *.webm")
        ])
        if not video:
            return
        
        output = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav"), ("AAC", "*.aac")]
        )
        if not output:
            return
        
        try:
            subprocess.run([
                "ffmpeg", "-i", video, "-vn", "-acodec", "libmp3lame",
                "-q:a", "2", "-y", output
            ], check=True, capture_output=True)
            messagebox.showinfo("Succès", f"Audio extrait: {output}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def start_conversion(self):
        """Démarrer la conversion"""
        if not self.files:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné !")
            return
        
        format_out = self.selected_format.get()
        options = self.options_panel.get_options()
        
        # Fenêtre de progression
        progress_window = ProgressWindow(self, len(self.files))
        
        # Thread de conversion
        thread = threading.Thread(
            target=self._convert_files,
            args=(format_out, options, progress_window)
        )
        thread.start()
    
    def _convert_files(self, format_out: str, options: ConversionOptions, progress_window: ProgressWindow):
        """Convertir les fichiers (thread)"""
        success = 0
        errors = 0
        
        for i, filepath in enumerate(self.files):
            if progress_window.cancelled:
                break
            
            filename = Path(filepath).name
            self.after(0, lambda f=filename, idx=i: progress_window.update_progress(idx, f))
            
            try:
                output = self._convert_single(filepath, format_out, options)
                ConversionHistory.add(filepath, str(output), format_out, True)
                success += 1
                self.after(0, lambda f=filename: progress_window.add_log(f"✅ {f}"))
            except Exception as e:
                ConversionHistory.add(filepath, "", format_out, False)
                errors += 1
                self.after(0, lambda f=filename, err=str(e): progress_window.add_log(f"❌ {f}: {err}"))
        
        self.after(0, lambda: progress_window.complete(success, errors))
        self.after(0, self.clear_files)
    
    def _convert_single(self, input_path: str, format_out: str, options: ConversionOptions) -> Path:
        """Convertir un fichier"""
        input_path = Path(input_path)
        input_ext = input_path.suffix.lower()[1:]
        
        # Nom de sortie avec préfixe/suffixe
        output_name = f"{options.prefix}{input_path.stem}{options.suffix}"
        
        # Extraire audio
        if format_out == "extract_audio":
            format_out = "mp3"
        
        output_path = self.output_folder / f"{output_name}.{format_out}"
        
        # Éviter conflits
        counter = 1
        while output_path.exists():
            output_path = self.output_folder / f"{output_name} ({counter}).{format_out}"
            counter += 1
        
        # === IMAGES ===
        if format_out in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "webp", "heic"]:
            img = Image.open(str(input_path))
            
            # Redimensionner
            if options.resize_width and options.resize_height:
                if options.keep_aspect_ratio:
                    img.thumbnail((options.resize_width, options.resize_height), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((options.resize_width, options.resize_height), Image.Resampling.LANCZOS)
            
            # Convertir mode si nécessaire
            if format_out in ["jpg", "jpeg"] and img.mode in ["RGBA", "P"]:
                img = img.convert("RGB")
            
            # Sauvegarder
            if format_out == "webp":
                img.save(str(output_path), "WEBP", quality=options.quality)
            elif format_out == "heic":
                subprocess.run(["sips", "-s", "format", "heic", str(input_path), "--out", str(output_path)],
                             check=True, capture_output=True)
            elif format_out in ["jpg", "jpeg"]:
                img.save(str(output_path), "JPEG", quality=options.quality)
            else:
                img.save(str(output_path))
        
        # === IMAGE vers PDF ===
        elif format_out == "pdf" and input_ext in ["png", "jpg", "jpeg", "gif", "tiff", "bmp", "webp"]:
            img = Image.open(str(input_path))
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(str(output_path), "PDF", resolution=100.0)
        
        # === AUDIO ===
        elif format_out in ["mp3", "wav", "aac", "flac", "m4a"]:
            cmd = ["ffmpeg", "-i", str(input_path), "-y"]
            
            if format_out == "mp3":
                cmd += ["-codec:a", "libmp3lame", "-b:a", options.bitrate_audio]
            elif format_out == "wav":
                cmd += ["-codec:a", "pcm_s16le"]
            elif format_out == "flac":
                cmd += ["-codec:a", "flac"]
            elif format_out in ["aac", "m4a"]:
                cmd += ["-codec:a", "aac", "-b:a", options.bitrate_audio]
            
            cmd.append(str(output_path))
            subprocess.run(cmd, check=True, capture_output=True)
        
        # === VIDÉO ===
        elif format_out in ["mp4", "mov", "avi", "mkv", "webm"]:
            cmd = ["ffmpeg", "-i", str(input_path), "-y"]
            
            if format_out == "mp4":
                cmd += ["-codec:v", "libx264", "-preset", "medium", "-crf", "23",
                       "-codec:a", "aac", "-b:a", options.bitrate_audio]
            elif format_out == "webm":
                cmd += ["-codec:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
                       "-codec:a", "libopus"]
            else:
                cmd += ["-codec:v", "copy", "-codec:a", "copy"]
            
            cmd.append(str(output_path))
            subprocess.run(cmd, check=True, capture_output=True)
        
        # === ARCHIVES ===
        elif format_out == "unzip":
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
            return output_dir
        
        elif format_out in ["zip", "tar", "7z"]:
            if format_out == "zip":
                subprocess.run(["zip", "-r", str(output_path), input_path.name],
                             cwd=str(input_path.parent), check=True, capture_output=True)
            elif format_out == "tar":
                subprocess.run(["tar", "-cvf", str(output_path), "-C", str(input_path.parent), input_path.name],
                             check=True, capture_output=True)
            elif format_out == "7z":
                subprocess.run(["7z", "a", str(output_path), str(input_path)],
                             check=True, capture_output=True)
        
        # === DOCUMENTS ===
        elif format_out in ["pdf", "docx", "txt", "html", "md"]:
            soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            
            if input_ext == "pdf" and format_out == "docx" and os.path.exists(soffice):
                subprocess.run([
                    soffice, "--headless", "--infilter=writer_pdf_import",
                    "--convert-to", "docx", "--outdir", str(self.output_folder), str(input_path)
                ], check=True, capture_output=True)
            elif format_out == "pdf" and os.path.exists(soffice):
                subprocess.run([
                    soffice, "--headless", "--convert-to", "pdf",
                    "--outdir", str(self.output_folder), str(input_path)
                ], check=True, capture_output=True)
            elif shutil.which("pandoc"):
                subprocess.run(["pandoc", str(input_path), "-o", str(output_path)],
                             check=True, capture_output=True)
            else:
                raise Exception("LibreOffice ou Pandoc requis")
        
        return output_path


def main():
    app = FormatConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
