//
//  ContentView.swift
//  FormatConverter
//
//  Vue principale avec interface drag & drop style Apple
//

import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @EnvironmentObject var conversionManager: ConversionManager
    @State private var isDragging = false
    @State private var selectedOutputFormat: OutputFormat = .pdf
    
    var body: some View {
        ZStack {
            // Fond avec effet vitrail macOS
            VisualEffectView(material: .sidebar, blendingMode: .behindWindow)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Barre de titre personnalisée
                CustomTitleBar()
                
                // Contenu principal
                HStack(spacing: 0) {
                    // Sidebar gauche - Formats de sortie
                    FormatSidebar(selectedFormat: $selectedOutputFormat)
                        .frame(width: 220)
                    
                    Divider()
                    
                    // Zone principale
                    VStack(spacing: 20) {
                        // Zone de drop
                        DropZoneView(isDragging: $isDragging)
                            .onDrop(of: [.fileURL], isTargeted: $isDragging) { providers in
                                handleDrop(providers: providers)
                                return true
                            }
                        
                        // Liste des fichiers en attente
                        if !conversionManager.pendingFiles.isEmpty {
                            FileListView()
                            
                            // Bouton de conversion
                            ConvertButton(outputFormat: selectedOutputFormat)
                        }
                        
                        // Historique des conversions
                        if !conversionManager.completedConversions.isEmpty {
                            CompletedConversionsView()
                        }
                    }
                    .padding(24)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
        }
        .alert("Erreur", isPresented: $conversionManager.showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(conversionManager.errorMessage)
        }
    }
    
    private func handleDrop(providers: [NSItemProvider]) {
        for provider in providers {
            provider.loadItem(forTypeIdentifier: UTType.fileURL.identifier, options: nil) { item, error in
                guard let data = item as? Data,
                      let url = URL(dataRepresentation: data, relativeTo: nil) else { return }
                
                DispatchQueue.main.async {
                    conversionManager.addFile(url: url)
                }
            }
        }
    }
}

// MARK: - Barre de titre personnalisée
struct CustomTitleBar: View {
    var body: some View {
        HStack {
            Spacer()
            
            Text("Format Converter")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            
            Spacer()
        }
        .frame(height: 52)
        .background(
            VisualEffectView(material: .titlebar, blendingMode: .withinWindow)
        )
    }
}

// MARK: - Sidebar des formats
struct FormatSidebar: View {
    @Binding var selectedFormat: OutputFormat
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("FORMAT DE SORTIE")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(.secondary)
                .padding(.horizontal, 16)
                .padding(.top, 20)
                .padding(.bottom, 12)
            
            ScrollView {
                VStack(spacing: 4) {
                    ForEach(OutputFormat.Category.allCases, id: \.self) { category in
                        FormatCategorySection(
                            category: category,
                            selectedFormat: $selectedFormat
                        )
                    }
                }
                .padding(.horizontal, 8)
            }
        }
        .background(
            VisualEffectView(material: .sidebar, blendingMode: .behindWindow)
        )
    }
}

struct FormatCategorySection: View {
    let category: OutputFormat.Category
    @Binding var selectedFormat: OutputFormat
    @State private var isExpanded = true
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isExpanded.toggle()
                }
            } label: {
                HStack {
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.secondary)
                        .frame(width: 16)
                    
                    Text(category.displayName)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.primary)
                    
                    Spacer()
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 8)
            }
            .buttonStyle(.plain)
            
            if isExpanded {
                ForEach(OutputFormat.allCases.filter { $0.category == category }, id: \.self) { format in
                    FormatRow(format: format, isSelected: selectedFormat == format)
                        .onTapGesture {
                            selectedFormat = format
                        }
                }
            }
        }
    }
}

struct FormatRow: View {
    let format: OutputFormat
    let isSelected: Bool
    
    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: format.iconName)
                .font(.system(size: 14))
                .foregroundColor(isSelected ? .white : format.color)
                .frame(width: 24)
            
            Text(format.displayName)
                .font(.system(size: 13))
                .foregroundColor(isSelected ? .white : .primary)
            
            Spacer()
            
            Text(format.rawValue.uppercased())
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(isSelected ? .white.opacity(0.8) : .secondary)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isSelected ? Color.accentColor : Color.clear)
        )
        .contentShape(Rectangle())
    }
}

// MARK: - Zone de Drop
struct DropZoneView: View {
    @Binding var isDragging: Bool
    @EnvironmentObject var conversionManager: ConversionManager
    
    var body: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(isDragging ? Color.accentColor.opacity(0.15) : Color.secondary.opacity(0.08))
                    .frame(width: 80, height: 80)
                
                Image(systemName: isDragging ? "arrow.down.doc.fill" : "plus.circle.fill")
                    .font(.system(size: 36))
                    .foregroundColor(isDragging ? .accentColor : .secondary)
                    .scaleEffect(isDragging ? 1.1 : 1.0)
                    .animation(.spring(response: 0.3), value: isDragging)
            }
            
            VStack(spacing: 6) {
                Text(isDragging ? "Déposez vos fichiers ici" : "Glissez-déposez vos fichiers")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(.primary)
                
                Text("ou cliquez pour parcourir")
                    .font(.system(size: 13))
                    .foregroundColor(.secondary)
            }
            
            Button {
                conversionManager.openFilePicker()
            } label: {
                Text("Parcourir...")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.accentColor)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(
                        RoundedRectangle(cornerRadius: 6)
                            .stroke(Color.accentColor, lineWidth: 1)
                    )
            }
            .buttonStyle(.plain)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 220)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(
                    isDragging ? Color.accentColor : Color.secondary.opacity(0.3),
                    style: StrokeStyle(lineWidth: 2, dash: [8])
                )
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(isDragging ? Color.accentColor.opacity(0.05) : Color.clear)
                )
        )
        .animation(.easeInOut(duration: 0.2), value: isDragging)
    }
}

// MARK: - Liste des fichiers
struct FileListView: View {
    @EnvironmentObject var conversionManager: ConversionManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Fichiers à convertir")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button {
                    conversionManager.clearPendingFiles()
                } label: {
                    Text("Tout effacer")
                        .font(.system(size: 12))
                        .foregroundColor(.red)
                }
                .buttonStyle(.plain)
            }
            
            ScrollView {
                VStack(spacing: 6) {
                    ForEach(conversionManager.pendingFiles) { file in
                        FileRow(file: file)
                    }
                }
            }
            .frame(maxHeight: 200)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color(NSColor.controlBackgroundColor))
        )
    }
}

struct FileRow: View {
    let file: PendingFile
    @EnvironmentObject var conversionManager: ConversionManager
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: file.iconName)
                .font(.system(size: 20))
                .foregroundColor(file.iconColor)
                .frame(width: 28)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(file.name)
                    .font(.system(size: 13, weight: .medium))
                    .lineLimit(1)
                
                Text(file.formattedSize)
                    .font(.system(size: 11))
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Button {
                conversionManager.removeFile(id: file.id)
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 16))
                    .foregroundColor(.secondary)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(NSColor.controlBackgroundColor))
        )
    }
}

// MARK: - Bouton de conversion
struct ConvertButton: View {
    let outputFormat: OutputFormat
    @EnvironmentObject var conversionManager: ConversionManager
    
    var body: some View {
        Button {
            conversionManager.convertFiles(to: outputFormat)
        } label: {
            HStack(spacing: 10) {
                if conversionManager.isConverting {
                    ProgressView()
                        .scaleEffect(0.8)
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: "arrow.triangle.2.circlepath")
                        .font(.system(size: 14, weight: .semibold))
                }
                
                Text(conversionManager.isConverting ? "Conversion en cours..." : "Convertir en \(outputFormat.displayName)")
                    .font(.system(size: 14, weight: .semibold))
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 44)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(conversionManager.isConverting ? Color.gray : Color.accentColor)
            )
        }
        .buttonStyle(.plain)
        .disabled(conversionManager.isConverting)
    }
}

// MARK: - Conversions terminées
struct CompletedConversionsView: View {
    @EnvironmentObject var conversionManager: ConversionManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Conversions terminées")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button {
                    conversionManager.clearCompletedConversions()
                } label: {
                    Text("Effacer")
                        .font(.system(size: 12))
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            
            ScrollView {
                VStack(spacing: 6) {
                    ForEach(conversionManager.completedConversions) { conversion in
                        CompletedConversionRow(conversion: conversion)
                    }
                }
            }
            .frame(maxHeight: 150)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.green.opacity(0.1))
        )
    }
}

struct CompletedConversionRow: View {
    let conversion: CompletedConversion
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 18))
                .foregroundColor(.green)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(conversion.outputName)
                    .font(.system(size: 13, weight: .medium))
                    .lineLimit(1)
                
                Text(conversion.formattedDate)
                    .font(.system(size: 11))
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Button {
                NSWorkspace.shared.selectFile(conversion.outputURL.path, inFileViewerRootedAtPath: "")
            } label: {
                Image(systemName: "folder")
                    .font(.system(size: 14))
                    .foregroundColor(.accentColor)
            }
            .buttonStyle(.plain)
            .help("Afficher dans le Finder")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(NSColor.controlBackgroundColor))
        )
    }
}

// MARK: - Visual Effect View (NSVisualEffectView wrapper)
struct VisualEffectView: NSViewRepresentable {
    let material: NSVisualEffectView.Material
    let blendingMode: NSVisualEffectView.BlendingMode
    
    func makeNSView(context: Context) -> NSVisualEffectView {
        let view = NSVisualEffectView()
        view.material = material
        view.blendingMode = blendingMode
        view.state = .active
        return view
    }
    
    func updateNSView(_ nsView: NSVisualEffectView, context: Context) {
        nsView.material = material
        nsView.blendingMode = blendingMode
    }
}

// MARK: - Preview
#Preview {
    ContentView()
        .environmentObject(ConversionManager())
        .frame(width: 900, height: 700)
}
