#!/usr/bin/env python3
"""Générateur d'icône pour Format Converter"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Créer l'icône de l'application"""
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        # Créer l'image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fond avec dégradé (simulé avec rectangle arrondi)
        padding = size // 10
        
        # Rectangle arrondi bleu
        corner_radius = size // 5
        
        # Dessiner le fond
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=corner_radius,
            fill=(10, 132, 255, 255)  # Bleu Apple
        )
        
        # Dessiner les flèches de conversion (cercle avec flèches)
        center = size // 2
        arrow_radius = size // 4
        
        # Cercle de flèches
        arrow_width = max(2, size // 20)
        
        # Arc supérieur
        draw.arc(
            [center - arrow_radius, center - arrow_radius, 
             center + arrow_radius, center + arrow_radius],
            start=220, end=320,
            fill=(255, 255, 255, 255),
            width=arrow_width
        )
        
        # Arc inférieur
        draw.arc(
            [center - arrow_radius, center - arrow_radius, 
             center + arrow_radius, center + arrow_radius],
            start=40, end=140,
            fill=(255, 255, 255, 255),
            width=arrow_width
        )
        
        # Triangles pour les pointes de flèches
        triangle_size = size // 10
        
        # Flèche haut droite
        x1, y1 = center + arrow_radius - triangle_size//2, center - arrow_radius//2
        draw.polygon([
            (x1, y1 - triangle_size),
            (x1 + triangle_size, y1),
            (x1, y1 + triangle_size//2)
        ], fill=(255, 255, 255, 255))
        
        # Flèche bas gauche
        x2, y2 = center - arrow_radius + triangle_size//2, center + arrow_radius//2
        draw.polygon([
            (x2, y2 + triangle_size),
            (x2 - triangle_size, y2),
            (x2, y2 - triangle_size//2)
        ], fill=(255, 255, 255, 255))
        
        # Sauvegarder
        img.save(f'/Users/jb/FormatConverter/icons/icon_{size}x{size}.png')
        
        if size == 512:
            img.save('/Users/jb/FormatConverter/icons/AppIcon.png')
    
    print("✅ Icônes créées dans /Users/jb/FormatConverter/icons/")

if __name__ == "__main__":
    os.makedirs('/Users/jb/FormatConverter/icons', exist_ok=True)
    create_icon()
