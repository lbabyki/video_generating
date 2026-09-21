"""Local, human-gated dataset governance; it never scrapes or downloads assets."""
from __future__ import annotations
import hashlib
import struct
from dataclasses import dataclass, replace
from pathlib import Path

STATES=("QUARANTINED","VALIDATED","CULTURAL_REVIEWED","APPROVED","REJECTED","BLOCKED")
_NEXT={"QUARANTINED":{"VALIDATED","REJECTED","BLOCKED"},"VALIDATED":{"CULTURAL_REVIEWED","REJECTED","BLOCKED"},"CULTURAL_REVIEWED":{"APPROVED","REJECTED","BLOCKED"}}
LICENSE_BLOCKED={"UNKNOWN","REJECTED","NO_TRAINING_PERMISSION","REQUIRES_LEGAL_REVIEW"}
ENV_LABELS={"flat_alluvial_plain","rice_paddy","river_dike","red_clay_tile_house","bamboo_hedge","banyan_tree","northern_vietnamese_communal_house","rural_boat"}

@dataclass(frozen=True)
class DatasetVersion:
    id:str; version:int; kind:str; trigger_word:str; state:str="DRAFT"
    def freeze(self)->"DatasetVersion": return replace(self,state="IMMUTABLE")
    def revise(self)->"DatasetVersion":
        if self.state=="IMMUTABLE": return DatasetVersion(self.id,self.version+1,self.kind,self.trigger_word)
        raise ValueError("only immutable dataset versions may be revised")

@dataclass(frozen=True)
class DatasetAsset:
    id:str; dataset_id:str; filename:str; sha256:str; perceptual_hash:str; dimensions:tuple[int,int]; source_url:str; source_type:str; creator:str; license_id:str; license_url:str; ml_training_permission:str; commercial_use_status:str; consent_status:str; caption_vi:str=""; caption_en:str=""; cultural_labels:tuple[str,...]=(); review_status:str="QUARANTINED"; reviewer_audit:str=""; source_group:str=""
    def transition(self,target:str,reviewer:str="")->"DatasetAsset":
        if target not in _NEXT.get(self.review_status,set()): raise ValueError("invalid dataset asset review transition")
        if target=="APPROVED" and (not reviewer or not self.caption_vi or not self.caption_en): raise ValueError("approval requires reviewer audit and bilingual factual captions")
        if target=="CULTURAL_REVIEWED" and any(x not in ENV_LABELS for x in self.cultural_labels): raise ValueError("unreviewed cultural label")
        return replace(self,review_status=target,reviewer_audit=reviewer or self.reviewer_audit)
    def eligible(self)->bool:
        return self.review_status=="APPROVED" and self.ml_training_permission=="YES" and self.commercial_use_status not in LICENSE_BLOCKED and bool(self.source_url and self.creator and self.license_id and self.license_url)

def validate_path(root:Path, name:str)->Path:
    path=(root/name).resolve()
    if path.parent!=root.resolve(): raise ValueError("dataset path traversal")
    return path
def sha256(path:Path)->str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def validate_image(path:Path,min_width:int=512,min_height:int=512)->tuple[int,int]:
    if path.suffix.lower() not in {".png",".jpg",".jpeg",".webp"}: raise ValueError("only PNG/JPEG/WebP assets are allowed")
    raw=path.read_bytes()
    if path.suffix.lower()==".png" and raw[:8]==b"\x89PNG\r\n\x1a\n" and raw[12:16]==b"IHDR": w,h=struct.unpack(">II",raw[16:24])
    else: raise ValueError("corrupt or unsupported image encoding")
    if w<min_width or h<min_height: raise ValueError("image dimensions below configured minimum")
    return w,h
def near_duplicate(a:str,b:str,threshold:int=8)->bool: return sum(x!=y for x,y in zip(a,b))<=threshold
def training_export(assets:list[DatasetAsset])->list[DatasetAsset]: return [x for x in assets if x.eligible()]
def split_assets(assets:list[DatasetAsset])->tuple[list[DatasetAsset],list[DatasetAsset]]:
    train=[]; valid=[]; groups={}
    for x in assets:
        bucket=groups.setdefault(x.source_group, train if len(groups)%5 else valid); bucket.append(x)
    return train,valid
