import Foundation
import CoreGraphics
let args=CommandLine.arguments
guard args.count>=3 else { fatalError("Output and input PDF required") }
guard let context=CGContext(URL(fileURLWithPath:args[1]) as CFURL,mediaBox:nil,nil) else { fatalError("Cannot open output") }
for file in args.dropFirst(2) {
 guard let source=CGPDFDocument(URL(fileURLWithPath:file) as CFURL) else { fatalError("Cannot read PDF") }
 for i in 1...source.numberOfPages {
  guard let page=source.page(at:i) else { fatalError("Page absent") }
  var box=page.getBoxRect(.mediaBox)
  let data=NSData(bytes:&box,length:MemoryLayout<CGRect>.size)
  context.beginPDFPage([kCGPDFContextMediaBox as String:data] as CFDictionary)
  context.drawPDFPage(page)
  context.endPDFPage()
 }
}
context.closePDF()
print("CoreGraphics vector PDF merge finished")
