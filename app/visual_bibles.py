"""Deterministic, grounded visual bible materialization for successful plans."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (CharacterBible, EnvironmentBible, GroundingRequirement,
    PromptCompilationRecord, SceneVisualBinding, VisualBibleSet, VisualPromptPackage, VisualBibleReview)

FORBIDDEN = ["high mountains", "mountain valley", "stilt-house village", "Tây Bắc/Tây Nguyên architecture",
             "Chinese/Japanese palace architecture", "fake text", "watermark", "unrequested modern foreign landmark"]
PACKAGE_VERSION = "visual-prompt-package-v1"

def select_runtime_package(db: Session, scene_id: str) -> VisualPromptPackage | None:
    """Return the sole runtime package for a scene, never from a DRAFT Bible."""
    rows = list(db.scalars(select(VisualPromptPackage).join(VisualBibleSet, VisualPromptPackage.bible_set_id == VisualBibleSet.id).where(
        VisualPromptPackage.scene_id == scene_id,
        VisualPromptPackage.runtime_selectable.is_(True),
        VisualPromptPackage.activation_status == "ACTIVE",
        VisualPromptPackage.valid.is_(True),
        VisualBibleSet.status.in_(["APPROVED", "LOCKED"]),
    )))
    if len(rows) > 1:
        raise ValueError(f"duplicate runtime-selectable packages for scene {scene_id}")
    return rows[0] if rows else None

def activate_runtime_package(db: Session, package_id: str) -> VisualPromptPackage:
    """Atomically promote one package and clear other selectable packages for its scene."""
    package = db.get(VisualPromptPackage, package_id)
    if package is None: raise ValueError("package not found")
    bible = db.get(VisualBibleSet, package.bible_set_id)
    if bible is None or bible.status not in {"APPROVED", "LOCKED"} or package.governance_status != "APPROVED" or not package.release_eligible or not package.valid:
        raise ValueError("package is not eligible for runtime activation")
    for other in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.scene_id == package.scene_id, VisualPromptPackage.runtime_selectable.is_(True))):
        other.runtime_selectable = False; other.activation_status = "SUPERSEDED"
    package.runtime_selectable = True; package.activation_status = "ACTIVE"
    db.commit(); db.refresh(package); return package

def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

class VisualBibleService:
    def __init__(self, db: Session): self.db = db

    def materialize(self, compilation_id: str) -> VisualBibleSet:
        compilation = self.db.get(PromptCompilationRecord, compilation_id)
        if compilation is None: raise ValueError("compilation not found")
        if compilation.compilation_status != "SUCCEEDED" or not compilation.plan_json:
            raise ValueError("only SUCCEEDED compilations can materialize a visual bible")
        existing = self.db.scalar(select(VisualBibleSet).where(VisualBibleSet.compilation_id == compilation_id).order_by(VisualBibleSet.version.desc()))
        if existing: return existing
        plan = json.loads(compilation.plan_json)
        source_hash = hashlib.sha256(compilation.plan_json.encode()).hexdigest()
        bible_id = str(uuid5(NAMESPACE_URL, f"visual-bible:{compilation_id}:1"))
        try:
            bible = VisualBibleSet(id=bible_id, project_id=compilation_id, compilation_id=compilation_id, version=1,
                status="DRAFT", source_plan_hash=source_hash, cultural_profile_id=plan.get("cultural_profile_id"), cultural_profile_version="1")
            self.db.add(bible); self.db.flush()
            profile = plan.get("regional_environment_profile") or {}
            regional_id = profile.get("regional_environment_profile_id", "unresolved")
            for char in plan.get("characters", []):
                cid = char["character_id"]
                self.db.add(CharacterBible(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:character:{cid}")), bible_set_id=bible_id,
                    character_id=cid, semantic_key=cid, display_name=char["name"], role=char["role"], age_band=char["age_group"],
                    body_proportion_style="2D educational animation, age-appropriate proportions", face_description="Friendly neutral face; no sensitive inferred traits.",
                    hairstyle="Simple consistent hairstyle from storyboard; do not infer ethnicity.", wardrobe=char["clothing_description"],
                    footwear="Simple age-appropriate everyday footwear.", accessories="Only accessories explicitly required by the storyboard.",
                    primary_palette="Clear, friendly educational palette.", secondary_palette="Soft supporting colors.", expression_range="Attentive, cooperative, positive.",
                    pose_guidance="Natural educational actions; maintain continuity.", cultural_notes="No unsupported ethnic or historical claims.",
                    forbidden_variations="No age drift, identity drift, stereotype, or unrequested costume change.", reference_asset_ids="[]", review_status="PENDING",
                    provenance=_json({"source_plan_hash": source_hash, "source_character_id": cid})))
            envs = {e["environment_id"]: e for e in plan.get("environments", [])}
            locations = {l["scene_location_id"]: l for l in plan.get("scene_locations", [])}
            self.db.add(EnvironmentBible(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:environment:regional:{regional_id}")), bible_set_id=bible_id,
                environment_id=regional_id, canonical_name=profile.get("display_name", "Red River Delta regional profile"), regional_profile_id=regional_id,
                terrain=profile.get("terrain", "flat_delta"), architecture_guidance="Generic contemporary regional context only; unsupported historical claims remain pending.",
                vegetation_guidance="Region-compatible vegetation pending grounding.", water_features="Regional river and delta water features pending grounding.", road_path_guidance="Generic safe rural and school paths only.", season="UNSPECIFIED", weather="UNSPECIFIED",
                time_of_day_options="Daytime", lighting="Soft natural educational lighting.", visual_palette="Bright, calm greens and blues.", cultural_notes="PENDING human cultural review.", required_features=_json(profile.get("required_features", [])), forbidden_features=_json(FORBIDDEN),
                grounding_status="PENDING", review_status="PENDING", provenance=_json({"source_plan_hash": source_hash, "source_regional_profile_id": regional_id}), reference_asset_ids="[]"))
            for env_id, env in envs.items():
                loc = locations.get(env_id, {})
                self.db.add(EnvironmentBible(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:environment:{env_id}")), bible_set_id=bible_id,
                    environment_id=env_id, canonical_name=loc.get("name", env_id), regional_profile_id=regional_id, terrain=profile.get("terrain", "UNSPECIFIED"),
                    architecture_guidance="Use only generic, contemporary forms present in the storyboard; no unsupported historical claims.",
                    vegetation_guidance="Use region-compatible vegetation described by the plan; keep claims pending until grounded.",
                    water_features="Dòng sông only where the storyboard requires it.", road_path_guidance="Simple safe paths appropriate to the described location.", season="UNSPECIFIED", weather="Clear, friendly educational weather unless storyboard specifies otherwise.",
                    time_of_day_options="Daytime", lighting="Soft natural educational lighting.", visual_palette="Bright, calm greens and blues.", cultural_notes="PENDING human cultural review; no invented architecture or history.",
                    required_features=_json(env.get("required_elements", [])), forbidden_features=_json(sorted(set(FORBIDDEN + env.get("forbidden_elements", [])))),
                    grounding_status="PENDING", review_status="PENDING", provenance=_json({"source_plan_hash": source_hash, "source_environment_id": env_id}), reference_asset_ids="[]"))
            requirements = [("REGION", regional_id, "Đặc điểm địa hình Đồng bằng Bắc Bộ và flat_delta"),
                ("LOCATION", next(iter(envs), regional_id), "Hình thái ruộng lúa phù hợp vùng"), ("LOCATION", next(iter(envs), regional_id), "Đặc điểm bờ sông phù hợp vùng"),
                ("LOCATION", next(iter(envs), regional_id), "Kiến trúc trường học phù hợp bối cảnh"), ("REGION", regional_id, "Cây cối và cảnh quan phù hợp"),
                ("CHARACTER", plan.get("characters", [{}])[0].get("character_id", "unknown"), "Trang phục học sinh phù hợp độ tuổi lớp 4"), ("REGION", regional_id, "Các claim văn hóa chưa có nguồn")]
            for scope, scope_id, claim in requirements:
                self.db.add(GroundingRequirement(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:grounding:{scope}:{scope_id}:{claim}")), bible_set_id=bible_id, scope_type=scope, scope_id=scope_id, claim=claim, status="PENDING", source_reference_ids="[]", review_required=True))
            chars_by_id = {c["character_id"]: str(uuid5(NAMESPACE_URL, f"{bible_id}:character:{c['character_id']}")) for c in plan.get("characters", [])}
            env_bible_ids = {eid: str(uuid5(NAMESPACE_URL, f"{bible_id}:environment:{eid}")) for eid in envs}
            for scene in plan.get("scenes", []):
                chars = scene.get("character_ids", [])
                binding_material = {"scene_id": scene["scene_id"], "character_ids": chars, "location_id": scene["environment_id"], "source_plan_hash": source_hash}
                binding_hash = _hash(binding_material)
                self.db.add(SceneVisualBinding(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:binding:{scene['scene_id']}")), bible_set_id=bible_id, scene_id=scene["scene_id"], character_ids=_json(chars), location_id=scene["environment_id"], regional_profile_id=regional_id, character_bible_version=1, environment_bible_version=1, visual_style_profile_id=plan.get("visual_style_profile_id"), cultural_profile_id=plan.get("cultural_profile_id"), grounding_status=scene.get("grounding_status", "PENDING"), source_plan_hash=source_hash, binding_hash=binding_hash))
                env = envs.get(scene["environment_id"], {})
                positive = ", ".join(["2D educational animation", scene.get("visual_action", ""), *[c for c in chars], env.get("visual_description", "")])
                negative = ", ".join(FORBIDDEN)
                material = {"scene_id": scene["scene_id"], "positive": positive, "negative": negative, "chars": chars, "env": scene["environment_id"], "camera": scene.get("camera_shot"), "source": source_hash}
                self.db.add(VisualPromptPackage(id=str(uuid5(NAMESPACE_URL, f"{bible_id}:package:{scene['scene_id']}")), bible_set_id=bible_id, scene_id=scene["scene_id"], positive_prompt=positive, negative_prompt=negative, character_tokens=_json(chars), environment_tokens=_json([scene["environment_id"]]), composition=scene.get("visual_action", ""), camera_framing=scene.get("camera_shot", "WIDE"), lighting="Soft natural educational lighting.", color_palette="Bright, calm greens and blues.", required_cultural_features=_json(profile.get("required_features", [])), forbidden_features=_json(FORBIDDEN), base_model_id=None, base_model_hash=None, intended_style_lora_ids="[]", seed_placeholder="UNASSIGNED", package_version=PACKAGE_VERSION, package_hash=_hash(material), governance_status="DRAFT", release_eligible=False, keyframe_status="NOT_GENERATED", valid=True))
            self.db.commit(); self.db.refresh(bible); return bible
        except Exception:
            self.db.rollback(); raise

    def get(self, bible_set_id: str): return self.db.get(VisualBibleSet, bible_set_id)
    def submit_review(self, bible: VisualBibleSet):
        if bible.status != "DRAFT": raise ValueError("only DRAFT bible sets can enter review")
        bible.status = "IN_REVIEW"; self.db.commit(); self.db.refresh(bible); return bible
    def approve(self, bible: VisualBibleSet):
        self._assert_source(bible); self._assert_grounding(bible); self._assert_complete(bible)
        bible.status="APPROVED"; bible.approved_at=datetime.now(UTC); self.db.commit(); self.db.refresh(bible); return bible
    def lock(self, bible: VisualBibleSet):
        if bible.status != "APPROVED": raise ValueError("only APPROVED bible sets can be locked")
        self._assert_source(bible); self._assert_grounding(bible); self._assert_complete(bible)
        bible.status="LOCKED"; bible.locked_at=datetime.now(UTC); self.db.commit(); self.db.refresh(bible); return bible
    def invalidate(self, bible: VisualBibleSet):
        if bible.status == "LOCKED": raise ValueError("LOCKED bible sets are immutable")
        for p in self.db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id == bible.id)): p.valid=False
        self.db.commit(); return bible
    def _assert_source(self, bible):
        c=self.db.get(PromptCompilationRecord,bible.compilation_id)
        if not c or c.compilation_status != "SUCCEEDED" or not c.plan_json or hashlib.sha256(c.plan_json.encode()).hexdigest()!=bible.source_plan_hash: raise ValueError("source plan is missing, failed, or changed")
    def _assert_grounding(self,bible):
        if any(r.status == "PENDING" or r.review_required for r in self.db.scalars(select(GroundingRequirement).where(GroundingRequirement.bible_set_id==bible.id))): raise ValueError("grounding requirements are still pending")
    def _assert_complete(self,bible):
        chars=list(self.db.scalars(select(CharacterBible).where(CharacterBible.bible_set_id==bible.id)))
        envs=list(self.db.scalars(select(EnvironmentBible).where(EnvironmentBible.bible_set_id==bible.id)))
        reviews=list(self.db.scalars(select(VisualBibleReview).where(VisualBibleReview.bible_set_id==bible.id)))
        if len(chars) != 2 or len(envs) != 4 or any(x.review_status != "APPROVED" for x in chars+envs): raise ValueError("cultural or bible review is incomplete")
        if not any(x.target_type == "CULTURAL" and x.status == "APPROVED" for x in reviews): raise ValueError("cultural review is incomplete")

def bible_response(bible: VisualBibleSet, db: Session) -> dict:
    def row(item): return {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
    return {"id": bible.id, "project_id": bible.project_id, "compilation_id": bible.compilation_id, "version": bible.version, "status": bible.status, "source_plan_hash": bible.source_plan_hash, "cultural_profile_id": bible.cultural_profile_id, "cultural_profile_version": bible.cultural_profile_version,
        "characters": [row(x) for x in db.scalars(select(CharacterBible).where(CharacterBible.bible_set_id==bible.id))],
        "environments": [row(x) for x in db.scalars(select(EnvironmentBible).where(EnvironmentBible.bible_set_id==bible.id))],
        "scene_bindings": [row(x) for x in db.scalars(select(SceneVisualBinding).where(SceneVisualBinding.bible_set_id==bible.id))],
        "prompt_packages": [row(x) for x in db.scalars(select(VisualPromptPackage).where(VisualPromptPackage.bible_set_id==bible.id))],
        "grounding_requirements": [row(x) for x in db.scalars(select(GroundingRequirement).where(GroundingRequirement.bible_set_id==bible.id))]}
