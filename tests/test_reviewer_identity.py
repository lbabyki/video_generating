import pytest
from sqlalchemy import create_engine, select, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.models import Base, HumanReviewer, HumanReviewerAudit, GroundingRequirement, EvidenceLink
from app.reviewer_identity import bootstrap_reviewer, require_reviewer

def make_db():
 e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); event.listen(e,"connect",lambda c,_:c.execute("PRAGMA foreign_keys=ON")); Base.metadata.create_all(e); return e,sessionmaker(bind=e)()

def test_bootstrap_is_active_audited_and_idempotent():
 e,db=make_db(); a=bootstrap_reviewer(db,"  Lê Hoàng  Giang ","PROJECT_OWNER"); b=bootstrap_reviewer(db,"lê hoàng giang","project_owner")
 assert a.id==b.id and a.status=="ACTIVE" and len(list(db.scalars(select(HumanReviewer))))==1 and len(list(db.scalars(select(HumanReviewerAudit))))==1
 db.close();e.dispose()

def test_empty_name_and_invalid_role_rejected():
 e,db=make_db()
 with pytest.raises(ValueError): bootstrap_reviewer(db," ","PROJECT_OWNER")
 with pytest.raises(ValueError): bootstrap_reviewer(db,"Reviewer","UNKNOWN")
 db.close();e.dispose()

def test_missing_inactive_revoked_and_wrong_role_rejected():
 e,db=make_db(); owner=bootstrap_reviewer(db,"Owner","PROJECT_OWNER"); cultural=bootstrap_reviewer(db,"Cultural","CULTURAL_REVIEWER"); cultural.status="INACTIVE"; db.commit()
 with pytest.raises(ValueError): require_reviewer(db,"missing","evidence")
 with pytest.raises(ValueError): require_reviewer(db,cultural.id,"cultural")
 owner.status="REVOKED"; db.commit()
 with pytest.raises(ValueError): require_reviewer(db,owner.id,"evidence")
 with pytest.raises(ValueError): require_reviewer(db,cultural.id,"evidence")
 db.close();e.dispose()

def test_project_owner_and_cultural_role_rules():
 e,db=make_db(); owner=bootstrap_reviewer(db,"Owner","PROJECT_OWNER"); cultural=bootstrap_reviewer(db,"Cultural","CULTURAL_REVIEWER")
 assert require_reviewer(db,owner.id,"evidence").id==owner.id
 assert require_reviewer(db,owner.id,"character").id==owner.id
 assert require_reviewer(db,owner.id,"environment").id==owner.id
 assert require_reviewer(db,cultural.id,"cultural").id==cultural.id
 with pytest.raises(ValueError): require_reviewer(db,owner.id,"cultural")
 db.close();e.dispose()
