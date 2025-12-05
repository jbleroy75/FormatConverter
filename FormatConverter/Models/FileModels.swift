//
//  FileModels.swift
//  FormatConverter
//
//  Modèles pour les fichiers en attente et les conversions
//

import SwiftUI

// MARK: - Fichier en attente de conversion
struct PendingFile: Identifiable {
    let id = UUID()
    let url: URL
    let name: String
    let size: Int64
    let fileExtension: String
    
    init(url: URL) {
        self.url = url
        self.name = url.lastPathComponent
        self.fileExtension = url.pathExtension.lowercased()
        
        if let attributes = try? FileManager.default.attributesOfItem(atPath: url.path),
           let fileSize = attributes[.size] as? Int64 {
            self.size = fileSize
        } else {
            self.size = 0
        }
    }
    
    var formattedSize: String {
        ByteCountFormatter.string(fromByteCount: size, countStyle: .file)
    }
    
    var iconName: String {
        switch fileExtension {
        case "pdf":
            return "doc.fill"
        case "docx", "doc", "pages":
            return "doc.text.fill"
        case "txt", "md", "rtf":
            return "text.alignleft"
        case "html", "htm":
            return "globe"
        case "png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp", "heic":
            return "photo.fill"
        case "mp3", "wav", "aac", "flac", "ogg", "m4a":
            return "waveform"
        case "mp4", "mov", "avi", "mkv", "webm":
            return "film.fill"
        case "zip", "tar", "gz", "7z", "rar":
            return "archivebox.fill"
        case "json", "xml", "csv", "yaml", "plist":
            return "tablecells.fill"
        default:
            return "doc.fill"
        }
    }
    
    var iconColor: Color {
        switch fileExtension {
        case "pdf":
            return .red
        case "docx", "doc", "pages":
            return .blue
        case "txt", "md", "rtf", "html":
            return .gray
        case "png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp", "heic":
            return .cyan
        case "mp3", "wav", "aac", "flac", "ogg", "m4a":
            return .purple
        case "mp4", "mov", "avi", "mkv", "webm":
            return .orange
        case "zip", "tar", "gz", "7z", "rar":
            return .brown
        case "json", "xml", "csv", "yaml", "plist":
            return .green
        default:
            return .secondary
        }
    }
}

// MARK: - Conversion terminée
struct CompletedConversion: Identifiable {
    let id = UUID()
    let inputURL: URL
    let outputURL: URL
    let outputFormat: OutputFormat
    let timestamp: Date
    
    var inputName: String {
        inputURL.lastPathComponent
    }
    
    var outputName: String {
        outputURL.lastPathComponent
    }
    
    var formattedDate: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.locale = Locale(identifier: "fr_FR")
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: timestamp, relativeTo: Date())
    }
}

// MARK: - Résultat de conversion
enum ConversionResult {
    case success(outputURL: URL)
    case failure(error: ConversionError)
}

// MARK: - Erreurs de conversion
enum ConversionError: LocalizedError {
    case unsupportedConversion(from: String, to: String)
    case fileNotFound(path: String)
    case conversionFailed(reason: String)
    case toolNotInstalled(tool: String)
    case outputFolderNotWritable
    case cancelled
    
    var errorDescription: String? {
        switch self {
        case .unsupportedConversion(let from, let to):
            return "Conversion de \(from) vers \(to) non supportée"
        case .fileNotFound(let path):
            return "Fichier introuvable: \(path)"
        case .conversionFailed(let reason):
            return "Échec de la conversion: \(reason)"
        case .toolNotInstalled(let tool):
            return "Outil requis non installé: \(tool). Installez-le via Homebrew."
        case .outputFolderNotWritable:
            return "Impossible d'écrire dans le dossier de destination"
        case .cancelled:
            return "Conversion annulée"
        }
    }
}

// MARK: - État de progression
struct ConversionProgress: Identifiable {
    let id = UUID()
    let fileName: String
    var progress: Double
    var status: Status
    
    enum Status {
        case pending
        case converting
        case completed
        case failed(error: String)
    }
}
