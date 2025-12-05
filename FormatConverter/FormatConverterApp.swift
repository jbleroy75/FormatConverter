//
//  FormatConverterApp.swift
//  FormatConverter
//
//  Application principale de conversion de fichiers
//

import SwiftUI

@main
struct FormatConverterApp: App {
    @StateObject private var conversionManager = ConversionManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(conversionManager)
                .frame(minWidth: 800, minHeight: 600)
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("Ouvrir des fichiers...") {
                    conversionManager.openFilePicker()
                }
                .keyboardShortcut("o", modifiers: .command)
            }
        }
        
        Settings {
            SettingsView()
                .environmentObject(conversionManager)
        }
    }
}
