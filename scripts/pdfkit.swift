import Foundation
import AppKit
import PDFKit
import ImageIO

let args = CommandLine.arguments
guard args.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else { fatalError("PDF input and output directory required") }
let out = URL(fileURLWithPath: args[2], isDirectory: true)
try FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let chosen = args.count > 3 ? Set(args[3].split(separator: ",").compactMap { Int($0) }) : Set(1...doc.pageCount)
var text = "Pages: \(doc.pageCount)\n"
var metadata: [[String: Any]] = []
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    text += "\n=== Page \(i+1) ===\n" + (page.string ?? "[No extracted text]") + "\n"
    metadata.append(["page":i+1,"width_pt":box.width,"height_pt":box.height])
    if chosen.contains(i+1) {
        let scale = min(2.0, 1600.0 / max(box.width, box.height))
        let size = NSSize(width: box.width*scale,height: box.height*scale)
        let context = CGContext(data:nil,width:Int(size.width),height:Int(size.height),bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
        context.setFillColor(CGColor(gray:1,alpha:1))
        context.fill(CGRect(origin: .zero,size: size))
        context.scaleBy(x: scale,y: scale)
        context.translateBy(x: -box.minX,y: -box.minY)
        if let cgpage = page.pageRef {
            context.drawPDFPage(cgpage)
        } else {
            page.draw(with: .mediaBox,to: context)
        }
        let destination=CGImageDestinationCreateWithURL(out.appendingPathComponent(String(format:"page-%03d.png",i+1)) as CFURL,"public.png" as CFString,1,nil)!
        CGImageDestinationAddImage(destination,context.makeImage()!,nil)
        guard CGImageDestinationFinalize(destination) else { fatalError("PNG write failed") }
    }
}
try text.write(to: out.appendingPathComponent("text.txt"),atomically: true,encoding: .utf8)
let data = try JSONSerialization.data(withJSONObject: metadata,options: [.prettyPrinted,.sortedKeys])
try data.write(to: out.appendingPathComponent("pages.json"))
print("Read \(doc.pageCount) PDF pages; rendered \(chosen.count) selected pages to \(out.path)")
