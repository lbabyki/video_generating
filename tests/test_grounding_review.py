import hashlib
from pathlib import Path
import pytest
from sqlalchemy import create_engine, select, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.models import Base, ReferenceSource, GroundingRequirement
from app.grounding import register_local

def db():
 e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); event.listen(e,"connect",lambda c,_:c.execute("PRAGMA foreign_keys=ON")); Base.metadata.create_all(e); return e,sessionmaker(bind=e)()

def valid_file(root):
 p=root/"ref.png"; p.write_bytes(b"\x89PNG\r\n\x1a\n"+b"fixture"); return p

def test_local_source_registration_hash_is_deterministic_and_idempotent(tmp_path,monkeypatch):
 import app.grounding as g; monkeypatch.setattr(g,"REFERENCE_ROOT",tmp_path.resolve()); valid_file(tmp_path); e,s=db()
 payload={"title":"Fixture","local_relative_path":"ref.png","source_type":"VISUAL_REFERENCE","usage_permission":"REFERENCE_ONLY","license":"Fixture"}
 a=register_local(s,payload); b=register_local(s,payload)
 assert a.id==b.id and a.sha256==hashlib.sha256((tmp_path/"ref.png").read_bytes()).hexdigest(); s.close();e.dispose()

def test_path_traversal_symlink_and_mime_mismatch_blocked(tmp_path,monkeypatch):
 import app.grounding as g; monkeypatch.setattr(g,"REFERENCE_ROOT",tmp_path.resolve()); valid_file(tmp_path); outside=tmp_path.parent/"outside.png"; outside.write_bytes(b"x")
 try: (tmp_path/"link.png").symlink_to(outside)
 except OSError: pytest.skip("symlink unavailable")
 e,s=db()
 with pytest.raises(ValueError): register_local(s,{"local_relative_path":"../outside.png"})
 with pytest.raises(ValueError): register_local(s,{"local_relative_path":"link.png"})
 with pytest.raises(ValueError): register_local(s,{"local_relative_path":"ref.png","mime_type":"image/jpeg"})
 s.close();e.dispose()

def test_training_permission_policy():
 from app.grounding import training_allowed
 e,s=db(); assert training_allowed(ReferenceSource(id="a",title="a",source_url="x",provenance="{}",license="x",usage_permission="TRAINING_ALLOWED"))
 assert not training_allowed(ReferenceSource(id="b",title="b",source_url="x",provenance="{}",license="x",usage_permission="REFERENCE_ONLY")); s.close();e.dispose()
