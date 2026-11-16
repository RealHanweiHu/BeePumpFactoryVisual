from pathlib import Path
import json,subprocess,re
r=Path(__file__).resolve().parents[1]
items=[('IMPLEMENTATION_1F_8F.html','report'),('output/pdf/BeePump_1F_8F_Implementation_Design_V2.4.pdf','report'),('output/pdf/BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf','report'),('BeePump_1F_8F_Implementation_V2.4_Source.zip','other')]
request={'uploads':[{'local_path':str(r/p),'purpose':'create_library_file','library_artifact_type':typ} for p,typ in items]}
for p,_ in items:assert (r/p).is_file()
previous=r/'reports/library_delivery_v2.4.json'
first=r/'reports/library_delivery_v2.4.first_attempt.json'
if previous.exists() and not first.exists():first.write_bytes(previous.read_bytes())
run=subprocess.run(['python3','/tmp/beepump-library-v24-current-oixioltf/library_upload.py'],input=json.dumps(request),capture_output=True,text=True,cwd=r)
try:result=json.loads(run.stdout)
except Exception:result={'error':run.stdout or run.stderr,'exit_code':run.returncode}
previous.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
summary={'exit_code':run.returncode,'requested_files':[p for p,_ in items]}
if isinstance(result,dict):
 summary['status']=result.get('status',result.get('success'))
 summary['error']=re.sub(r'https?://\S+','[private transfer detail]',str(result.get('error',result.get('message',''))))[:700]
 summary['ordered_results']=[{k:v for k,v in item.items() if k in ['status','error','message','library_file_id','file_id','version','filename','local_path']} for item in result.get('results',[]) if isinstance(item,dict)]
print(json.dumps(summary,ensure_ascii=False,indent=2))
