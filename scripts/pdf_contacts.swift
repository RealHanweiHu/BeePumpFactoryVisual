import Foundation
import AppKit

let args = CommandLine.arguments
guard args.count == 2 else { fatalError("Usage: pdf_contacts.swift PDF_RENDER_DIRECTORY") }
let folder = URL(fileURLWithPath: args[1], isDirectory: true)
let files = try FileManager.default.contentsOfDirectory(at: folder, includingPropertiesForKeys: nil)
    .filter { $0.lastPathComponent.hasPrefix("page-") && $0.pathExtension == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
for offset in stride(from: 0, to: files.count, by: 6) {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: 2440, pixelsHigh: 2660, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    NSColor(calibratedWhite: 0.90, alpha: 1).setFill()
    NSBezierPath(rect: NSRect(x:0, y:0, width:2440, height:2660)).fill()
    for (i, url) in files[offset..<min(offset+6,files.count)].enumerated() {
        guard let bitmap=NSBitmapImageRep(data:try Data(contentsOf: url)), let cgImage=bitmap.cgImage else { fatalError("Missing PNG") }
        let img=NSImage(cgImage:cgImage,size:NSSize(width:Double(bitmap.pixelsWide),height:Double(bitmap.pixelsHigh)))
        let x=20+Double(i%2)*1210, y=2660-Double(i/2+1)*880+40
        img.draw(in:NSRect(x:x, y:y, width:1190, height:840), from:NSRect(origin:.zero,size:img.size), operation:.copy, fraction:1)
        let label=NSAttributedString(string:url.lastPathComponent,attributes:[.font:NSFont.systemFont(ofSize:20),.foregroundColor:NSColor.black])
        label.draw(at:NSPoint(x:x+12, y:y-27))
    }
    NSGraphicsContext.restoreGraphicsState()
    let dest=folder.appendingPathComponent(String(format:"contact-cg-%02d.png",offset/6+1))
    try rep.representation(using:.png,properties:[:])!.write(to:dest)
}
print("Created contacts for \(files.count) actual PDF page PNGs")
