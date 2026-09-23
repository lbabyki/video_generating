#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, hashlib, json, subprocess, time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
from sqlalchemy import select
from app.comfyui_client import ComfyArtifact, ComfyUIClient
from app.db.models import CharacterBible, CharacterReferenceCandidate, ModelRegistryEntry, VisualBibleReview, VisualBibleSet, VisualPromptPackage, EnvironmentBible
from app.db.session import SessionLocal
ROOT=Path(__file__).parents[1]; BIBLE_ID='9f2272dd-2237-53ed-a3aa-fd570e89a75e'; CHARACTER_ID='a0c4fcf8-2fa3-5119-9c60-67f9982ae182'; CHARACTER_BIBLE_ID='81b0b83f-d624-5ebc-879f-a6c7fb0ea850'; MODEL_ID='sdxl-base-1.0'; SEED=31415926
POSITIVE='Bright friendly 2D educational animation character design for Grade 4 learning, one Vietnamese primary school student, 8 to 10 years old, age-appropriate proportions, friendly neutral expression, standing naturally, full body, slight three-quarter front view, short-sleeved white collared shirt, dark navy trousers, simple shoes, neatly worn red scarf for a Young Pioneer student, clean simple clothing, plain light background, clear readable silhouette, soft natural colors, no text, no logo.'
NEGATIVE='multiple people, duplicate person, multiple views, character sheet grid, adult body proportions, teenager, preschool child, photorealistic, school logo, name badge, fake text, watermark, incorrect uniform, long-sleeved shirt, skirt, shorts, bright blue trousers, oversized red scarf, military uniform, distorted hands, extra fingers, extra limbs, cropped feet, complex background, Chinese school uniform, Japanese school uniform'
def gpu(): return subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.used,memory.total','--format=csv,noheader'],text=True,capture_output=True,check=True).stdout.strip()
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def wh(w): return hashlib.sha256(json.dumps(w,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def wf(ckpt): return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':ckpt}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':POSITIVE,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':NEGATIVE,'clip':['1',1]}},'4':{'class_type':'EmptyLatentImage','inputs':{'width':1024,'height':1024,'batch_size':1}},'5':{'class_type':'KSampler','inputs':{'seed':SEED,'steps':30,'cfg':6.0,'sampler_name':'euler','scheduler':'normal','denoise':1.0,'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['4',0]}},'6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},'7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':'phase3d/student-reference/candidate-001/student-reference'}}}
async def run(url,timeout):
 outdir=ROOT/'output/phase3d/student-reference/candidate-001'; outdir.mkdir(parents=True,exist_ok=True)
 if any(outdir.iterdir()): raise RuntimeError('candidate-001 output directory is not empty; refusing overwrite')
 with SessionLocal() as db:
  bible=db.get(VisualBibleSet,BIBLE_ID); char=db.get(CharacterBible,CHARACTER_BIBLE_ID); model=db.get(ModelRegistryEntry,MODEL_ID); cultural=db.scalar(select(VisualBibleReview).where(VisualBibleReview.bible_set_id==BIBLE_ID,VisualBibleReview.target_type=='CULTURAL',VisualBibleReview.status=='APPROVED_WITH_RESTRICTED_SCOPE')); envs=list(db.scalars(select(EnvironmentBible).where(EnvironmentBible.bible_set_id==BIBLE_ID))); v4=list(db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==BIBLE_ID,VisualPromptPackage.package_version=='visual-prompt-package-v4')))
  if not bible or bible.status!='APPROVED' or not char or char.review_status!='APPROVED' or not cultural: raise RuntimeError('approval preflight failed')
  if not model or model.sha256!='31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b': raise RuntimeError('model registry preflight failed')
  if len(envs)!=4 or any(e.review_status!='APPROVED' for e in envs): raise RuntimeError('environment preflight failed')
  if len(v4)!=8 or any(p.package_status!='ACTIVE' or p.governance_status!='DRAFT' or p.keyframe_status!='NOT_GENERATED' for p in v4): raise RuntimeError('v4 package preflight failed')
  local=ROOT/'models/checkpoints'/model.local_filename
  if sh(local)!=model.sha256: raise RuntimeError('local checkpoint hash mismatch')
  rev=(ROOT/'docker/comfyui/COMFYUI_REVISION').read_text().strip()
 before=gpu(); w=wf(model.local_filename); wsha=wh(w); start=time.monotonic(); observed=[before]
 async with ComfyUIClient(url) as client:
  pid=await client.submit(w,'phase3d-student-reference-candidate-001'); history={}
  for _ in range(timeout):
   history=await client.history(pid)
   if pid in history: break
   observed.append(gpu()); await asyncio.sleep(1)
  else: raise TimeoutError('candidate job timed out; no retry permitted')
  imgs=history[pid].get('outputs',{}).get('7',{}).get('images',[])
  if len(imgs)!=1: raise RuntimeError(f'expected exactly one output image, got {len(imgs)}')
  im=imgs[0]; artifact=ComfyArtifact(im['filename'],im.get('subfolder',''),im.get('type','output')); content=await client.artifact(artifact)
 elapsed=int((time.monotonic()-start)*1000); after=gpu(); output=ROOT/'output'/artifact.subfolder/artifact.filename
 if not output.is_file() or output.read_bytes()!=content: raise RuntimeError('artifact/local output mismatch')
 if not output.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'): raise RuntimeError('output is not PNG')
 info=subprocess.run(['identify','-format','%w %h %[channels]',str(output)],text=True,capture_output=True,check=True).stdout.strip().split()
 if info[:2] != ['1024','1024']: raise RuntimeError(f'unexpected image dimensions: {info}')
 dims=(int(info[0]),int(info[1])); mode=info[2] if len(info)>2 else 'unknown'
 digest=sh(output); relative=str(output.relative_to(ROOT)); cid=str(uuid5(NAMESPACE_URL,f'character-reference:{digest}')); now=datetime.now(UTC).isoformat()
 metadata={'candidate_id':cid,'character_bible_id':CHARACTER_BIBLE_ID,'character_id':CHARACTER_ID,'character_bible_version':2,'bible_set_id':BIBLE_ID,'bible_set_version':bible.version,'base_model_id':model.id,'base_model_revision':model.source_revision,'base_model_sha256':model.sha256,'checkpoint_filename':model.source_filename,'architecture':model.architecture,'positive_prompt':POSITIVE,'negative_prompt':NEGATIVE,'workflow_version':'phase3d-student-reference-v1','workflow_sha256':wsha,'seed':SEED,'sampler':'euler','scheduler':'normal','steps':30,'cfg':6.0,'width':dims[0],'height':dims[1],'mode':mode,'output_relative_path':relative,'output_sha256':digest,'comfyui_revision':rev,'prompt_id':pid,'latency_ms':elapsed,'vram_before':before,'vram_observed':observed,'vram_after':after,'governance_status':'DRAFT','human_review_status':'PENDING','reference_status':'CANDIDATE','release_eligible':False,'lora_status':'NOT_ASSIGNED','created_at':now}
 (outdir/'candidate-001.metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 with SessionLocal() as db:
  db.add(CharacterReferenceCandidate(id=cid,character_bible_id=CHARACTER_BIBLE_ID,character_id=CHARACTER_ID,character_bible_version=2,bible_set_id=BIBLE_ID,bible_set_version=bible.version,base_model_id=model.id,base_model_revision=model.source_revision,base_model_sha256=model.sha256,positive_prompt=POSITIVE,negative_prompt=NEGATIVE,workflow_version='phase3d-student-reference-v1',workflow_sha256=wsha,seed=SEED,sampler='euler',scheduler='normal',steps=30,cfg=6.0,width=dims[0],height=dims[1],output_relative_path=relative,output_sha256=digest,comfyui_revision=rev,latency_ms=elapsed,vram_before=before,vram_peak=max(observed+[before]),vram_after=after,governance_status='DRAFT',human_review_status='PENDING',reference_status='CANDIDATE',release_eligible=False,lora_status='NOT_ASSIGNED')); db.commit()
 print(json.dumps(metadata,ensure_ascii=False,sort_keys=True))
def main():
 p=argparse.ArgumentParser(); p.add_argument('--comfyui-url',default='http://127.0.0.1:8188'); p.add_argument('--timeout',type=int,default=900); a=p.parse_args(); asyncio.run(run(a.comfyui_url,a.timeout))
if __name__=='__main__': main()
