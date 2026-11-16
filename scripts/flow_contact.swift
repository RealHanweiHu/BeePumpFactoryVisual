import Foundation
import AppKit
import ImageIO
let args=CommandLine.arguments
guard args.count>2 else{fatalError("input dir and output dir required")}
let source=URL(fileURLWithPath:args[1]), out=URL(fileURLWithPath:args[2])
try FileManager.default.createDirectory(at:out,withIntermediateDirectories:true)
let files=try FileManager.default.contentsOfDirectory(at:source,includingPropertiesForKeys:nil).filter{$0.lastPathComponent.hasPrefix("page-") && $0.pathExtension=="png"}.sorted{$0.lastPathComponent<$1.lastPathComponent}
for start in stride(from:0,to:files.count,by:6){
 let items=Array(files[start..<min(start+6,files.count)])
 let context=CGContext(data:nil,width:1800,height:900,bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
 context.setFillColor(CGColor(gray:0.85,alpha:1));context.fill(CGRect(x:0,y:0,width:1800,height:900))
 for (i,url) in items.enumerated(){
  let image=CGImageSourceCreateImageAtIndex(CGImageSourceCreateWithURL(url as CFURL,nil)!,0,nil)!
  let width=580.0,height=580.0*Double(image.height)/Double(image.width)
  let x=Double(i%3)*600+10,y=900-Double(i/3+1)*450+20
  context.draw(image,in:CGRect(x:x,y:y,width:width,height:height))
 }
 let url=out.appendingPathComponent(String(format:"contact-%02d.png",start/6+1))
 let dest=CGImageDestinationCreateWithURL(url as CFURL,"public.png" as CFString,1,nil)!
 CGImageDestinationAddImage(dest,context.makeImage()!,nil)
 guard CGImageDestinationFinalize(dest) else{fatalError("contact PNG write failed")}
}
print("Created \((files.count+5)/6) contact sheets for \(files.count) pages")
