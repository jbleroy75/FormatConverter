//
//  SettingsView.swift
//  FormatConverter
//
//  Vue des préférences de l'application
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var conversionManager: ConversionManager
    @AppStorage("outputFolder") var outputFolderPath: String = ""
    @AppStorage("openAfterConversion") var openAfterConversion: Bool = true
    @AppStorage("showNotifications") var showNotifications: Bool = true
    @AppStorage("deleteOriginalAfterConversion") var deleteOriginal: Bool = false
    
    var body: some View {
        TabView {
            GeneralSettingsView(
                outputFolderPath: $outputFolderPath,
                openAfterConversion: $openAfterConversion,
                showNotifications: $showNotifications,
                deleteOriginal: $deleteOriginal,
                conversionManager: conversionManager
            )
            .tabItem {
                Label("Général", systemImage: "gear")
            }
            
            ToolsSettingsView()
                .tabItem {
                    Label("Outils", systemImage: "wrench.and.screwdriver")
                }
            
            AboutView()
                .tabItem {
                    Label("À propos", systemImage: "info.circle")
                }
        }
        .frame(width: 500, height: 400)
    }
}

// MARK: - Paramètres généraux

struct GeneralSettingsView: View {
    @Binding var outputFolderPath: String
    @Binding var openAfterConversion: Bool
    @Binding var showNotifications: Bool
    @Binding var deleteOriginal: Bool
    var conversionManager: ConversionManager
    
    var body: some View {
        Form {
            Section {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Dossier de sortie")
                            .font(.headline)
                        
                        Text(outputFolderPath.isEmpty ? "Téléchargements (par défaut)" : outputFolderPath)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                            .truncationMode(.middle)
                    }
                    
                    Spacer()
                    
                    Button("Choisir...") {
                        conversionManager.selectOutputFolder()
                    }
                    
                    if !outputFolderPath.isEmpty {
                        Button {
                            outputFolderPath = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.vertical, 8)
            }
            
            Section {
                Toggle(isOn: $openAfterConversion) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Ouvrir le dossier après conversion")
                        Text("Affiche le Finder avec les fichiers convertis")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Toggle(isOn: $showNotifications) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Afficher les notifications")
                        Text("Notification à la fin de chaque conversion")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Toggle(isOn: $deleteOriginal) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Supprimer l'original après conversion")
                            .foregroundColor(deleteOriginal ? .red : .primary)
                        Text("⚠️ Cette action est irréversible")
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

// MARK: - Paramètres des outils

struct ToolsSettingsView: View {
    @State private var toolsStatus: [String: Bool] = [:]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Outils de conversion installés")
                .font(.headline)
            
            Text("Certaines conversions nécessitent des outils externes. Installez-les via Homebrew.")
                .font(.caption)
                .foregroundColor(.secondary)
            
            ScrollView {
                VStack(spacing: 12) {
                    ToolRow(
                        name: "FFmpeg",
                        description: "Conversion audio/vidéo",
                        installCommand: "brew install ffmpeg",
                        isInstalled: toolsStatus["ffmpeg"] ?? false
                    )
                    
                    ToolRow(
                        name: "Pandoc",
                        description: "Conversion de documents",
                        installCommand: "brew install pandoc",
                        isInstalled: toolsStatus["pandoc"] ?? false
                    )
                    
                    ToolRow(
                        name: "LibreOffice",
                        description: "Documents Office (Word, Excel)",
                        installCommand: "brew install --cask libreoffice",
                        isInstalled: toolsStatus["libreoffice"] ?? false
                    )
                    
                    ToolRow(
                        name: "7-Zip",
                        description: "Archives 7z",
                        installCommand: "brew install p7zip",
                        isInstalled: toolsStatus["7z"] ?? false
                    )
                    
                    ToolRow(
                        name: "Unar",
                        description: "Archives RAR",
                        installCommand: "brew install unar",
                        isInstalled: toolsStatus["unar"] ?? false
                    )
                    
                    ToolRow(
                        name: "WebP",
                        description: "Images WebP",
                        installCommand: "brew install webp",
                        isInstalled: toolsStatus["webp"] ?? false
                    )
                }
            }
            
            HStack {
                Spacer()
                Button {
                    checkTools()
                } label: {
                    Label("Vérifier les outils", systemImage: "arrow.clockwise")
                }
            }
        }
        .padding()
        .onAppear {
            checkTools()
        }
    }
    
    private func checkTools() {
        let fm = FileManager.default
        
        toolsStatus["ffmpeg"] = fm.fileExists(atPath: "/usr/local/bin/ffmpeg") || fm.fileExists(atPath: "/opt/homebrew/bin/ffmpeg")
        toolsStatus["pandoc"] = fm.fileExists(atPath: "/usr/local/bin/pandoc") || fm.fileExists(atPath: "/opt/homebrew/bin/pandoc")
        toolsStatus["libreoffice"] = fm.fileExists(atPath: "/Applications/LibreOffice.app")
        toolsStatus["7z"] = fm.fileExists(atPath: "/usr/local/bin/7z") || fm.fileExists(atPath: "/opt/homebrew/bin/7z")
        toolsStatus["unar"] = fm.fileExists(atPath: "/usr/local/bin/unar") || fm.fileExists(atPath: "/opt/homebrew/bin/unar")
        toolsStatus["webp"] = fm.fileExists(atPath: "/usr/local/bin/cwebp") || fm.fileExists(atPath: "/opt/homebrew/bin/cwebp")
    }
}

struct ToolRow: View {
    let name: String
    let description: String
    let installCommand: String
    let isInstalled: Bool
    
    @State private var isCopied = false
    
    var body: some View {
        HStack {
            Image(systemName: isInstalled ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundColor(isInstalled ? .green : .red)
                .font(.system(size: 20))
            
            VStack(alignment: .leading, spacing: 2) {
                Text(name)
                    .font(.system(size: 13, weight: .medium))
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            if !isInstalled {
                Button {
                    NSPasteboard.general.clearContents()
                    NSPasteboard.general.setString(installCommand, forType: .string)
                    isCopied = true
                    
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        isCopied = false
                    }
                } label: {
                    Text(isCopied ? "Copié !" : "Copier commande")
                        .font(.caption)
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(NSColor.controlBackgroundColor))
        )
    }
}

// MARK: - À propos

struct AboutView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "arrow.triangle.2.circlepath.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(
                    LinearGradient(
                        colors: [.blue, .purple],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
            
            VStack(spacing: 4) {
                Text("Format Converter")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Version 1.0.0")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text("Convertissez tous vos fichiers en quelques clics.\nDocuments, images, audio, vidéo, archives et plus encore.")
                .font(.body)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal, 40)
            
            Divider()
                .padding(.horizontal, 60)
            
            VStack(spacing: 8) {
                Text("Formats supportés")
                    .font(.headline)
                
                HStack(spacing: 20) {
                    FormatBadge(category: "Documents", count: 9, color: .red)
                    FormatBadge(category: "Images", count: 10, color: .blue)
                    FormatBadge(category: "Audio", count: 7, color: .purple)
                }
                
                HStack(spacing: 20) {
                    FormatBadge(category: "Vidéo", count: 7, color: .orange)
                    FormatBadge(category: "Archives", count: 6, color: .brown)
                    FormatBadge(category: "Données", count: 5, color: .green)
                }
            }
            
            Spacer()
            
            Text("© 2024 - Application macOS native")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

struct FormatBadge: View {
    let category: String
    let count: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 2) {
            Text("\(count)")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(color)
            
            Text(category)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(width: 80)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(color.opacity(0.1))
        )
    }
}

#Preview {
    SettingsView()
        .environmentObject(ConversionManager())
}
