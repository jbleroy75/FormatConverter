//
//  OutputFormat.swift
//  FormatConverter
//
//  Définition des formats de sortie supportés
//

import SwiftUI

enum OutputFormat: String, CaseIterable, Identifiable {
    // Documents
    case pdf = "pdf"
    case docx = "docx"
    case doc = "doc"
    case txt = "txt"
    case rtf = "rtf"
    case odt = "odt"
    case html = "html"
    case md = "md"
    case epub = "epub"
    
    // Images
    case png = "png"
    case jpg = "jpg"
    case jpeg = "jpeg"
    case gif = "gif"
    case webp = "webp"
    case tiff = "tiff"
    case bmp = "bmp"
    case heic = "heic"
    case ico = "ico"
    case svg = "svg"
    
    // Audio
    case mp3 = "mp3"
    case wav = "wav"
    case aac = "aac"
    case flac = "flac"
    case ogg = "ogg"
    case m4a = "m4a"
    case wma = "wma"
    
    // Vidéo
    case mp4 = "mp4"
    case mov = "mov"
    case avi = "avi"
    case mkv = "mkv"
    case webm = "webm"
    case wmv = "wmv"
    case flv = "flv"
    
    // Archives
    case zip = "zip"
    case unzip = "unzip"
    case tar = "tar"
    case gz = "gz"
    case sevenZ = "7z"
    case rar = "rar"
    
    // Données
    case json = "json"
    case xml = "xml"
    case csv = "csv"
    case yaml = "yaml"
    case plist = "plist"
    
    var id: String { rawValue }
    
    enum Category: String, CaseIterable {
        case documents = "Documents"
        case images = "Images"
        case audio = "Audio"
        case video = "Vidéo"
        case archives = "Archives"
        case data = "Données"
        
        var displayName: String { rawValue }
    }
    
    var category: Category {
        switch self {
        case .pdf, .docx, .doc, .txt, .rtf, .odt, .html, .md, .epub:
            return .documents
        case .png, .jpg, .jpeg, .gif, .webp, .tiff, .bmp, .heic, .ico, .svg:
            return .images
        case .mp3, .wav, .aac, .flac, .ogg, .m4a, .wma:
            return .audio
        case .mp4, .mov, .avi, .mkv, .webm, .wmv, .flv:
            return .video
        case .zip, .unzip, .tar, .gz, .sevenZ, .rar:
            return .archives
        case .json, .xml, .csv, .yaml, .plist:
            return .data
        }
    }
    
    var displayName: String {
        switch self {
        case .pdf: return "PDF"
        case .docx: return "Word (DOCX)"
        case .doc: return "Word (DOC)"
        case .txt: return "Texte brut"
        case .rtf: return "Rich Text"
        case .odt: return "OpenDocument"
        case .html: return "HTML"
        case .md: return "Markdown"
        case .epub: return "EPUB"
        case .png: return "PNG"
        case .jpg, .jpeg: return "JPEG"
        case .gif: return "GIF"
        case .webp: return "WebP"
        case .tiff: return "TIFF"
        case .bmp: return "Bitmap"
        case .heic: return "HEIC"
        case .ico: return "Icône"
        case .svg: return "SVG"
        case .mp3: return "MP3"
        case .wav: return "WAV"
        case .aac: return "AAC"
        case .flac: return "FLAC"
        case .ogg: return "OGG"
        case .m4a: return "M4A"
        case .wma: return "WMA"
        case .mp4: return "MP4"
        case .mov: return "QuickTime"
        case .avi: return "AVI"
        case .mkv: return "MKV"
        case .webm: return "WebM"
        case .wmv: return "WMV"
        case .flv: return "FLV"
        case .zip: return "ZIP"
        case .unzip: return "Décompresser"
        case .tar: return "TAR"
        case .gz: return "GZIP"
        case .sevenZ: return "7-Zip"
        case .rar: return "RAR"
        case .json: return "JSON"
        case .xml: return "XML"
        case .csv: return "CSV"
        case .yaml: return "YAML"
        case .plist: return "Property List"
        }
    }
    
    var iconName: String {
        switch category {
        case .documents:
            switch self {
            case .pdf: return "doc.fill"
            case .docx, .doc: return "doc.text.fill"
            case .txt, .md: return "text.alignleft"
            case .html: return "globe"
            case .epub: return "book.fill"
            default: return "doc.fill"
            }
        case .images:
            return "photo.fill"
        case .audio:
            return "waveform"
        case .video:
            return "film.fill"
        case .archives:
            if self == .unzip {
                return "archivebox"
            }
            return "archivebox.fill"
        case .data:
            return "tablecells.fill"
        }
    }
    
    var color: Color {
        switch category {
        case .documents: return .red
        case .images: return .blue
        case .audio: return .purple
        case .video: return .orange
        case .archives: return .brown
        case .data: return .green
        }
    }
    
    var fileExtension: String {
        switch self {
        case .sevenZ: return "7z"
        case .unzip: return "" // Spécial - extraction
        default: return rawValue
        }
    }
}

// MARK: - Extensions pour la détection du type de fichier
extension OutputFormat {
    static func detectInputFormat(from url: URL) -> String {
        url.pathExtension.lowercased()
    }
    
    static func canConvert(from inputExtension: String, to output: OutputFormat) -> Bool {
        let input = inputExtension.lowercased()
        
        // Archives - décompression
        if output == .unzip {
            return ["zip", "tar", "gz", "7z", "rar", "tar.gz", "tgz"].contains(input)
        }
        
        // Documents
        let documentFormats = ["pdf", "docx", "doc", "txt", "rtf", "odt", "html", "md", "epub", "pages"]
        if output.category == .documents && documentFormats.contains(input) {
            return true
        }
        
        // Images
        let imageFormats = ["png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp", "heic", "ico", "svg", "raw", "cr2", "nef"]
        if output.category == .images && imageFormats.contains(input) {
            return true
        }
        
        // Audio
        let audioFormats = ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma", "aiff"]
        if output.category == .audio && audioFormats.contains(input) {
            return true
        }
        
        // Vidéo
        let videoFormats = ["mp4", "mov", "avi", "mkv", "webm", "wmv", "flv", "m4v"]
        if output.category == .video && videoFormats.contains(input) {
            return true
        }
        
        // Archives - compression
        if output.category == .archives && output != .unzip {
            return true // On peut toujours compresser n'importe quoi
        }
        
        // Données
        let dataFormats = ["json", "xml", "csv", "yaml", "yml", "plist"]
        if output.category == .data && dataFormats.contains(input) {
            return true
        }
        
        return false
    }
}
