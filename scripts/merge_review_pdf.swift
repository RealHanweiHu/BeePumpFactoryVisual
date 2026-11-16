import Foundation
import PDFKit
let args=CommandLine.arguments
guard args.count >= 3 else { fatalError("output and input PDFs required") }
let output=PDFDocument()
let inputs=args.dropFirst(2).map { file -> PDFDocument in
 guard let doc=PDFDocument(url:URL(fileURLWithPath:file)) else { fatalError("Cannot read \(file)") }
 return doc
}
for doc in inputs {
 for index in 0..<doc.pageCount {
  guard let page=doc.page(at:index) else { fatalError("Missing page") }
  output.insert(page,at:output.pageCount)
 }
}
guard withExtendedLifetime(inputs,{output.write(to:URL(fileURLWithPath:args[1]))}) else { fatalError("Cannot write PDF") }
print("Merged \(output.pageCount) pages")
