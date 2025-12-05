//
//  ConversionManager.swift
//  FormatConverter
//
//  Gestionnaire principal des conversions
//

import SwiftUI
import AppKit
import UniformTypeIdentifiers

@MainActor
class ConversionManager: ObservableObject {
    @Published var pendingFiles: [PendingFile] = []
    @Published var completedConversions: [CompletedConversion] = []
    @Published var isConverting = false
    @Published var showError = false
    @Published var errorMessage = ""
    @Published var conversionProgress: [ConversionProgress] = []
    
    @AppStorage("outputFolder") var outputFolderPath: String = ""
    @AppStorage("openAfterConversion") var openAfterConversion: Bool = true
    
    private let converter = FileConverter()
    
    var outputFolder: URL {
        if !outputFolderPath.isEmpty {
            return URL(fileURLWithPath: outputFolderPath)
        }
        return FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask).first!
    }
    
    // MARK: - Gestion des fichiers
    
    func addFile(url: URL) {
        // Éviter les doublons
        guard !pendingFiles.contains(where: { $0.url == url }) else { return }
        
        let file = PendingFile(url: url)
        pendingFiles.append(file)
    }
    
    func removeFile(id: UUID) {
        pendingFiles.removeAll { $0.id == id }
    }
    
    func clearPendingFiles() {
        pendingFiles.removeAll()
    }
    
    func clearCompletedConversions() {
        completedConversions.removeAll()
    }
    
    // MARK: - Sélecteur de fichiers
    
    func openFilePicker() {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = true
        panel.canChooseDirectories = false
        panel.canChooseFiles = true
        panel.message = "Sélectionnez les fichiers à convertir"
        panel.prompt = "Ajouter"
        
        panel.begin { [weak self] response in
            guard response == .OK else { return }
            
            Task { @MainActor in
                for url in panel.urls {
                    self?.addFile(url: url)
                }
            }
        }
    }
    
    func selectOutputFolder() {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.canCreateDirectories = true
        panel.message = "Sélectionnez le dossier de destination"
        panel.prompt = "Choisir"
        
        panel.begin { [weak self] response in
            guard response == .OK, let url = panel.url else { return }
            
            Task { @MainActor in
                self?.outputFolderPath = url.path
            }
        }
    }
    
    // MARK: - Conversion
    
    func convertFiles(to format: OutputFormat) {
        guard !pendingFiles.isEmpty else { return }
        
        isConverting = true
        let filesToConvert = pendingFiles
        
        Task {
            var successCount = 0
            var errors: [String] = []
            
            for file in filesToConvert {
                do {
                    let result = try await converter.convert(file: file, to: format, outputFolder: outputFolder)
                    
                    let completed = CompletedConversion(
                        inputURL: file.url,
                        outputURL: result,
                        outputFormat: format,
                        timestamp: Date()
                    )
                    
                    await MainActor.run {
                        completedConversions.insert(completed, at: 0)
                        pendingFiles.removeAll { $0.id == file.id }
                    }
                    
                    successCount += 1
                    
                } catch {
                    errors.append("\(file.name): \(error.localizedDescription)")
                }
            }
            
            await MainActor.run {
                isConverting = false
                
                if !errors.isEmpty {
                    errorMessage = errors.joined(separator: "\n")
                    showError = true
                }
                
                // Ouvrir le dossier de sortie si demandé
                if openAfterConversion && successCount > 0 {
                    NSWorkspace.shared.open(outputFolder)
                }
            }
        }
    }
}
