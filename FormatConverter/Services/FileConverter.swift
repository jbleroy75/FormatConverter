//
//  FileConverter.swift
//  FormatConverter
//
//  Moteur de conversion utilisant les outils système et externes
//

import Foundation
import AppKit
import PDFKit

@MainActor
class FileConverter {
    
    // MARK: - Conversion principale
    
    func convert(file: PendingFile, to format: OutputFormat, outputFolder: URL) async throws -> URL {
        // Vérifier si la conversion est supportée
        guard OutputFormat.canConvert(from: file.fileExtension, to: format) || format.category == .archives else {
            throw ConversionError.unsupportedConversion(from: file.fileExtension, to: format.rawValue)
        }
        
        // Générer le nom de sortie
        let outputName = file.url.deletingPathExtension().lastPathComponent
        var outputURL: URL
        
        if format == .unzip {
            outputURL = outputFolder.appendingPathComponent(outputName)
        } else {
            outputURL = outputFolder.appendingPathComponent("\(outputName).\(format.fileExtension)")
        }
        
        // Éviter les conflits de noms
        outputURL = makeUniqueURL(outputURL)
        
        // Router vers le bon convertisseur
        switch format.category {
        case .documents:
            return try await convertDocument(from: file.url, to: format, output: outputURL)
        case .images:
            return try await convertImage(from: file.url, to: format, output: outputURL)
        case .audio:
            return try await convertAudio(from: file.url, to: format, output: outputURL)
        case .video:
            return try await convertVideo(from: file.url, to: format, output: outputURL)
        case .archives:
            if format == .unzip {
                return try await extractArchive(from: file.url, to: outputURL)
            } else {
                return try await createArchive(from: file.url, format: format, output: outputURL)
            }
        case .data:
            return try await convertData(from: file.url, to: format, output: outputURL)
        }
    }
    
    // MARK: - Conversion de documents
    
    private func convertDocument(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        // PDF via système
        if format == .pdf {
            return try await convertToPDF(from: input, output: output)
        }
        
        // Texte simple
        if format == .txt {
            return try extractText(from: input, output: output)
        }
        
        // HTML
        if format == .html {
            return try await convertToHTML(from: input, output: output)
        }
        
        // Markdown
        if format == .md {
            return try await convertToMarkdown(from: input, output: output)
        }
        
        // Pour les conversions complexes, utiliser pandoc ou LibreOffice
        if isPandocAvailable() {
            return try await convertWithPandoc(from: input, to: format, output: output)
        }
        
        if isLibreOfficeAvailable() {
            return try await convertWithLibreOffice(from: input, to: format, output: output)
        }
        
        throw ConversionError.toolNotInstalled(tool: "pandoc ou LibreOffice")
    }
    
    private func convertToPDF(from input: URL, output: URL) async throws -> URL {
        let inputExtension = input.pathExtension.lowercased()
        
        // Images vers PDF avec CGContext
        if ["png", "jpg", "jpeg", "tiff", "bmp", "gif"].contains(inputExtension) {
            guard let image = NSImage(contentsOf: input) else {
                throw ConversionError.fileNotFound(path: input.path)
            }
            
            let pdfData = NSMutableData()
            guard let pdfConsumer = CGDataConsumer(data: pdfData as CFMutableData) else {
                throw ConversionError.conversionFailed(reason: "Impossible de créer le consumer PDF")
            }
            
            var mediaBox = CGRect(origin: .zero, size: image.size)
            guard let pdfContext = CGContext(consumer: pdfConsumer, mediaBox: &mediaBox, nil) else {
                throw ConversionError.conversionFailed(reason: "Impossible de créer le contexte PDF")
            }
            
            pdfContext.beginPage(mediaBox: &mediaBox)
            
            if let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) {
                pdfContext.draw(cgImage, in: mediaBox)
            }
            
            pdfContext.endPage()
            pdfContext.closePDF()
            
            try pdfData.write(to: output)
            return output
        }
        
        // Texte vers PDF avec PDFKit
        if ["txt", "md", "rtf"].contains(inputExtension) {
            let content = try String(contentsOf: input, encoding: .utf8)
            let pdfData = createPDFFromText(content)
            try pdfData.write(to: output)
            return output
        }
        
        // Pour docx/doc, utiliser LibreOffice ou pandoc
        if isLibreOfficeAvailable() {
            return try await convertWithLibreOffice(from: input, to: .pdf, output: output)
        }
        
        if isPandocAvailable() {
            return try await convertWithPandoc(from: input, to: .pdf, output: output)
        }
        
        throw ConversionError.conversionFailed(reason: "Format d'entrée non supporté pour la conversion PDF")
    }
    
    private func createPDFFromText(_ text: String) -> Data {
        // Créer un PDF simple avec Core Graphics
        let pageWidth: CGFloat = 595  // A4
        let pageHeight: CGFloat = 842
        let margin: CGFloat = 50
        
        let pdfData = NSMutableData()
        var mediaBox = CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight)
        
        guard let consumer = CGDataConsumer(data: pdfData as CFMutableData),
              let context = CGContext(consumer: consumer, mediaBox: &mediaBox, nil) else {
            return Data()
        }
        
        let font = CTFontCreateWithName("Menlo" as CFString, 11, nil)
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.lineBreakMode = .byWordWrapping
        
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: NSColor.black,
            .paragraphStyle: paragraphStyle
        ]
        
        let attrString = NSAttributedString(string: text, attributes: attributes)
        let framesetter = CTFramesetterCreateWithAttributedString(attrString)
        
        var currentIndex = 0
        let textLength = attrString.length
        
        while currentIndex < textLength {
            context.beginPage(mediaBox: &mediaBox)
            
            let framePath = CGPath(rect: CGRect(x: margin, y: margin, width: pageWidth - 2*margin, height: pageHeight - 2*margin), transform: nil)
            let frame = CTFramesetterCreateFrame(framesetter, CFRange(location: currentIndex, length: 0), framePath, nil)
            
            CTFrameDraw(frame, context)
            
            let frameRange = CTFrameGetVisibleStringRange(frame)
            currentIndex += frameRange.length
            
            if frameRange.length == 0 {
                break // Éviter boucle infinie
            }
            
            context.endPage()
        }
        
        context.closePDF()
        return pdfData as Data
    }
    
    private func extractText(from input: URL, output: URL) throws -> URL {
        let inputExtension = input.pathExtension.lowercased()
        var text = ""
        
        if inputExtension == "pdf" {
            guard let pdfDocument = PDFDocument(url: input) else {
                throw ConversionError.fileNotFound(path: input.path)
            }
            
            for i in 0..<pdfDocument.pageCount {
                if let page = pdfDocument.page(at: i), let pageText = page.string {
                    text += pageText + "\n\n"
                }
            }
        } else if inputExtension == "rtf" {
            let rtfData = try Data(contentsOf: input)
            if let attrString = NSAttributedString(rtf: rtfData, documentAttributes: nil) {
                text = attrString.string
            }
        } else {
            text = try String(contentsOf: input, encoding: .utf8)
        }
        
        try text.write(to: output, atomically: true, encoding: .utf8)
        return output
    }
    
    private func convertToHTML(from input: URL, output: URL) async throws -> URL {
        let inputExtension = input.pathExtension.lowercased()
        
        if inputExtension == "md" {
            let markdown = try String(contentsOf: input, encoding: .utf8)
            let html = convertMarkdownToHTML(markdown)
            try html.write(to: output, atomically: true, encoding: .utf8)
            return output
        }
        
        if isPandocAvailable() {
            return try await convertWithPandoc(from: input, to: .html, output: output)
        }
        
        // Conversion basique
        let text = try String(contentsOf: input, encoding: .utf8)
        let html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>\(input.deletingPathExtension().lastPathComponent)</title>
        </head>
        <body>
            <pre>\(text.htmlEscaped)</pre>
        </body>
        </html>
        """
        try html.write(to: output, atomically: true, encoding: .utf8)
        return output
    }
    
    private func convertToMarkdown(from input: URL, output: URL) async throws -> URL {
        if isPandocAvailable() {
            return try await convertWithPandoc(from: input, to: .md, output: output)
        }
        
        let text = try String(contentsOf: input, encoding: .utf8)
        try text.write(to: output, atomically: true, encoding: .utf8)
        return output
    }
    
    private func convertMarkdownToHTML(_ markdown: String) -> String {
        var html = markdown
        
        html = html.replacingOccurrences(of: "(?m)^### (.+)$", with: "<h3>$1</h3>", options: .regularExpression)
        html = html.replacingOccurrences(of: "(?m)^## (.+)$", with: "<h2>$1</h2>", options: .regularExpression)
        html = html.replacingOccurrences(of: "(?m)^# (.+)$", with: "<h1>$1</h1>", options: .regularExpression)
        html = html.replacingOccurrences(of: "\\*\\*(.+?)\\*\\*", with: "<strong>$1</strong>", options: .regularExpression)
        html = html.replacingOccurrences(of: "\\*(.+?)\\*", with: "<em>$1</em>", options: .regularExpression)
        html = html.replacingOccurrences(of: "\\[(.+?)\\]\\((.+?)\\)", with: "<a href=\"$2\">$1</a>", options: .regularExpression)
        html = html.replacingOccurrences(of: "\n\n", with: "</p><p>")
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }</style>
        </head>
        <body><p>\(html)</p></body>
        </html>
        """
    }
    
    // MARK: - Conversion d'images
    
    private func convertImage(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        guard let image = NSImage(contentsOf: input) else {
            throw ConversionError.fileNotFound(path: input.path)
        }
        
        guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            throw ConversionError.conversionFailed(reason: "Impossible de lire l'image")
        }
        
        let bitmapRep = NSBitmapImageRep(cgImage: cgImage)
        var imageData: Data?
        
        switch format {
        case .png:
            imageData = bitmapRep.representation(using: .png, properties: [:])
        case .jpg, .jpeg:
            imageData = bitmapRep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])
        case .gif:
            imageData = bitmapRep.representation(using: .gif, properties: [:])
        case .tiff:
            imageData = bitmapRep.representation(using: .tiff, properties: [:])
        case .bmp:
            imageData = bitmapRep.representation(using: .bmp, properties: [:])
        case .webp:
            if let cwebp = findTool("cwebp") {
                try await runCommand(cwebp, arguments: [input.path, "-o", output.path])
                return output
            }
            throw ConversionError.toolNotInstalled(tool: "cwebp (brew install webp)")
        case .heic:
            try await runCommand("/usr/bin/sips", arguments: ["-s", "format", "heic", input.path, "--out", output.path])
            return output
        default:
            throw ConversionError.unsupportedConversion(from: input.pathExtension, to: format.rawValue)
        }
        
        guard let data = imageData else {
            throw ConversionError.conversionFailed(reason: "Échec de l'encodage de l'image")
        }
        
        try data.write(to: output)
        return output
    }
    
    // MARK: - Conversion audio
    
    private func convertAudio(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        guard let ffmpeg = findTool("ffmpeg") else {
            throw ConversionError.toolNotInstalled(tool: "ffmpeg (brew install ffmpeg)")
        }
        
        var arguments = ["-i", input.path, "-y"]
        
        switch format {
        case .mp3:
            arguments += ["-codec:a", "libmp3lame", "-qscale:a", "2"]
        case .wav:
            arguments += ["-codec:a", "pcm_s16le"]
        case .flac:
            arguments += ["-codec:a", "flac"]
        case .ogg:
            arguments += ["-codec:a", "libvorbis", "-qscale:a", "5"]
        case .aac, .m4a:
            arguments += ["-codec:a", "aac", "-b:a", "256k"]
        default:
            break
        }
        
        arguments.append(output.path)
        try await runCommand(ffmpeg, arguments: arguments)
        return output
    }
    
    // MARK: - Conversion vidéo
    
    private func convertVideo(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        guard let ffmpeg = findTool("ffmpeg") else {
            throw ConversionError.toolNotInstalled(tool: "ffmpeg (brew install ffmpeg)")
        }
        
        var arguments = ["-i", input.path, "-y"]
        
        switch format {
        case .mp4:
            arguments += ["-codec:v", "libx264", "-preset", "medium", "-crf", "23", "-codec:a", "aac", "-b:a", "128k"]
        case .mov:
            arguments += ["-codec:v", "prores_ks", "-profile:v", "3", "-codec:a", "pcm_s16le"]
        case .webm:
            arguments += ["-codec:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-codec:a", "libopus"]
        case .avi:
            arguments += ["-codec:v", "mpeg4", "-q:v", "5", "-codec:a", "mp3"]
        case .mkv:
            arguments += ["-codec:v", "copy", "-codec:a", "copy"]
        default:
            break
        }
        
        arguments.append(output.path)
        try await runCommand(ffmpeg, arguments: arguments)
        return output
    }
    
    // MARK: - Archives
    
    private func extractArchive(from input: URL, to output: URL) async throws -> URL {
        let inputExtension = input.pathExtension.lowercased()
        
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
        
        switch inputExtension {
        case "zip":
            try await runCommand("/usr/bin/unzip", arguments: ["-o", input.path, "-d", output.path])
        case "tar":
            try await runCommand("/usr/bin/tar", arguments: ["-xf", input.path, "-C", output.path])
        case "gz", "tgz":
            try await runCommand("/usr/bin/tar", arguments: ["-xzf", input.path, "-C", output.path])
        case "7z":
            guard let sevenZ = findTool("7z") else {
                throw ConversionError.toolNotInstalled(tool: "7z (brew install p7zip)")
            }
            try await runCommand(sevenZ, arguments: ["x", input.path, "-o\(output.path)"])
        case "rar":
            guard let unar = findTool("unar") else {
                throw ConversionError.toolNotInstalled(tool: "unar (brew install unar)")
            }
            try await runCommand(unar, arguments: ["-o", output.path, input.path])
        default:
            throw ConversionError.unsupportedConversion(from: inputExtension, to: "extraction")
        }
        
        return output
    }
    
    private func createArchive(from input: URL, format: OutputFormat, output: URL) async throws -> URL {
        switch format {
        case .zip:
            try await runCommand("/usr/bin/zip", arguments: ["-r", output.path, input.lastPathComponent], workingDirectory: input.deletingLastPathComponent().path)
        case .tar:
            try await runCommand("/usr/bin/tar", arguments: ["-cvf", output.path, "-C", input.deletingLastPathComponent().path, input.lastPathComponent])
        case .gz:
            try await runCommand("/usr/bin/gzip", arguments: ["-c", input.path], outputFile: output)
        case .sevenZ:
            guard let sevenZ = findTool("7z") else {
                throw ConversionError.toolNotInstalled(tool: "7z (brew install p7zip)")
            }
            try await runCommand(sevenZ, arguments: ["a", output.path, input.path])
        default:
            throw ConversionError.unsupportedConversion(from: input.pathExtension, to: format.rawValue)
        }
        
        return output
    }
    
    // MARK: - Conversion de données
    
    private func convertData(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        let inputExtension = input.pathExtension.lowercased()
        let inputData = try Data(contentsOf: input)
        
        var jsonObject: Any?
        
        switch inputExtension {
        case "json":
            jsonObject = try JSONSerialization.jsonObject(with: inputData)
        case "plist":
            jsonObject = try PropertyListSerialization.propertyList(from: inputData, format: nil)
        case "csv":
            jsonObject = parseCSV(String(data: inputData, encoding: .utf8) ?? "")
        case "yaml", "yml":
            jsonObject = parseSimpleYAML(String(data: inputData, encoding: .utf8) ?? "")
        default:
            throw ConversionError.unsupportedConversion(from: inputExtension, to: format.rawValue)
        }
        
        guard let object = jsonObject else {
            throw ConversionError.conversionFailed(reason: "Impossible de parser le fichier")
        }
        
        let outputData: Data
        
        switch format {
        case .json:
            outputData = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
        case .plist:
            outputData = try PropertyListSerialization.data(fromPropertyList: object, format: .xml, options: 0)
        case .csv:
            outputData = convertToCSV(object).data(using: .utf8)!
        case .yaml:
            outputData = convertToYAML(object).data(using: .utf8)!
        case .xml:
            outputData = convertToXML(object).data(using: .utf8)!
        default:
            throw ConversionError.unsupportedConversion(from: inputExtension, to: format.rawValue)
        }
        
        try outputData.write(to: output)
        return output
    }
    
    private func parseCSV(_ csv: String) -> [[String: String]] {
        var result: [[String: String]] = []
        let lines = csv.components(separatedBy: .newlines).filter { !$0.isEmpty }
        guard lines.count > 1 else { return result }
        
        let headers = lines[0].components(separatedBy: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        
        for i in 1..<lines.count {
            let values = lines[i].components(separatedBy: ",").map { $0.trimmingCharacters(in: .whitespaces) }
            var row: [String: String] = [:]
            for (index, header) in headers.enumerated() where index < values.count {
                row[header] = values[index]
            }
            result.append(row)
        }
        return result
    }
    
    private func parseSimpleYAML(_ yaml: String) -> [String: String] {
        var result: [String: String] = [:]
        for line in yaml.components(separatedBy: .newlines) {
            let parts = line.split(separator: ":", maxSplits: 1)
            if parts.count == 2 {
                result[String(parts[0]).trimmingCharacters(in: .whitespaces)] = String(parts[1]).trimmingCharacters(in: .whitespaces)
            }
        }
        return result
    }
    
    private func convertToCSV(_ object: Any) -> String {
        guard let array = object as? [[String: Any]], let first = array.first else { return "" }
        let headers = Array(first.keys).sorted()
        var csv = headers.joined(separator: ",") + "\n"
        for item in array {
            csv += headers.map { item[$0].map { "\($0)" } ?? "" }.joined(separator: ",") + "\n"
        }
        return csv
    }
    
    private func convertToYAML(_ object: Any) -> String {
        var yaml = ""
        if let dict = object as? [String: Any] {
            for (key, value) in dict.sorted(by: { $0.key < $1.key }) {
                yaml += "\(key): \(value)\n"
            }
        }
        return yaml
    }
    
    private func convertToXML(_ object: Any) -> String {
        var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<root>\n"
        if let dict = object as? [String: Any] {
            for (key, value) in dict {
                xml += "  <\(key.replacingOccurrences(of: " ", with: "_"))>\(value)</\(key.replacingOccurrences(of: " ", with: "_"))>\n"
            }
        }
        return xml + "</root>"
    }
    
    // MARK: - Outils externes
    
    private func convertWithPandoc(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        guard let pandoc = findTool("pandoc") else {
            throw ConversionError.toolNotInstalled(tool: "pandoc")
        }
        
        let outputFormat: String
        switch format {
        case .pdf: outputFormat = "pdf"
        case .docx: outputFormat = "docx"
        case .html: outputFormat = "html"
        case .md: outputFormat = "markdown"
        case .txt: outputFormat = "plain"
        case .epub: outputFormat = "epub"
        default: throw ConversionError.unsupportedConversion(from: input.pathExtension, to: format.rawValue)
        }
        
        try await runCommand(pandoc, arguments: [input.path, "-o", output.path, "-t", outputFormat])
        return output
    }
    
    private func convertWithLibreOffice(from input: URL, to format: OutputFormat, output: URL) async throws -> URL {
        let loPath = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        
        let filterName: String
        switch format {
        case .pdf: filterName = "pdf"
        case .docx: filterName = "docx"
        case .odt: filterName = "odt"
        case .html: filterName = "html"
        case .txt: filterName = "txt"
        default: throw ConversionError.unsupportedConversion(from: input.pathExtension, to: format.rawValue)
        }
        
        try await runCommand(loPath, arguments: [
            "--headless", "--convert-to", filterName,
            "--outdir", output.deletingLastPathComponent().path, input.path
        ])
        
        return output
    }
    
    // MARK: - Utilitaires
    
    private func findTool(_ name: String) -> String? {
        ["/opt/homebrew/bin/\(name)", "/usr/local/bin/\(name)", "/usr/bin/\(name)"]
            .first { FileManager.default.fileExists(atPath: $0) }
    }
    
    private func isPandocAvailable() -> Bool { findTool("pandoc") != nil }
    private func isLibreOfficeAvailable() -> Bool { FileManager.default.fileExists(atPath: "/Applications/LibreOffice.app/Contents/MacOS/soffice") }
    
    private func runCommand(_ command: String, arguments: [String], workingDirectory: String? = nil, outputFile: URL? = nil) async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            DispatchQueue.global(qos: .userInitiated).async {
                let process = Process()
                process.executableURL = URL(fileURLWithPath: command)
                process.arguments = arguments
                
                if let workDir = workingDirectory {
                    process.currentDirectoryURL = URL(fileURLWithPath: workDir)
                }
                
                let outputPipe = Pipe()
                let errorPipe = Pipe()
                process.standardOutput = outputPipe
                process.standardError = errorPipe
                
                do {
                    try process.run()
                    process.waitUntilExit()
                    
                    if let outputFile = outputFile {
                        try outputPipe.fileHandleForReading.readDataToEndOfFile().write(to: outputFile)
                    }
                    
                    if process.terminationStatus != 0 {
                        let errorString = String(data: errorPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? "Erreur"
                        continuation.resume(throwing: ConversionError.conversionFailed(reason: errorString))
                    } else {
                        continuation.resume()
                    }
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    private func makeUniqueURL(_ url: URL) -> URL {
        var finalURL = url
        var counter = 1
        let baseName = url.deletingPathExtension().lastPathComponent
        let ext = url.pathExtension
        let directory = url.deletingLastPathComponent()
        
        while FileManager.default.fileExists(atPath: finalURL.path) {
            finalURL = ext.isEmpty
                ? directory.appendingPathComponent("\(baseName) (\(counter))")
                : directory.appendingPathComponent("\(baseName) (\(counter)).\(ext)")
            counter += 1
        }
        return finalURL
    }
}

extension String {
    var htmlEscaped: String {
        self.replacingOccurrences(of: "&", with: "&amp;")
            .replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")
    }
}
