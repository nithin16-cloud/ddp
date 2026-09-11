import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Test, TestParameter, User, UserRole
from schemas import TestCreate, TestUpdate, TestOut, TestParameterCreate, TestParameterOut
from dependencies import require_role

router = APIRouter(prefix="/tests", tags=["Tests Catalog"])


# ==================== Levenshtein Distance & Fuzzy Match Engine ====================

def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculates normalized Levenshtein similarity ratio between 0.0 and 1.0."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )
    dist = dp[len1][len2]
    max_len = max(len1, len2)
    return round(1.0 - (dist / max_len), 3)


CLINICAL_ALIASES: Dict[str, List[str]] = {
    "cbc": ["cbc", "complete blood count", "hemogram", "blood count", "hb", "hemoglobin", "platelets", "wbc", "rbc", "pcv"],
    "lipid": ["lipid", "lipid profile", "cholesterol", "chol", "triglycerides", "tg", "hdl", "ldl", "vldl", "cardiac lipid"],
    "thyroid": ["thyroid", "tft", "tsh", "thyroid profile", "t3", "t4", "ultrasensitive tsh"],
    "hba1c": ["hba1c", "glycated hemoglobin", "estimated glucose", "eag", "sugar", "fbs", "ppbs", "diabetes", "blood sugar", "fasting sugar"],
    "lft": ["lft", "liver function", "sgot", "sgpt", "alt", "ast", "bilirubin", "bili", "liver enzymes", "hepatic"],
    "kft": ["kft", "kidney function", "creatinine", "sr creatinine", "serum creatinine", "urea", "bun", "uric acid", "renal profile"],
    "vitd_b12": ["vitamin d", "vit d", "vitamin b12", "vit b12", "b12", "d3", "cholecalciferol", "cyanocobalamin", "vitality duo"]
}


class PrescriptionParseRequest(BaseModel):
    prescription_text: str


@router.post("/parse-prescription")
def parse_prescription_text(req: PrescriptionParseRequest, db: Session = Depends(get_db)):
    """
    Parses informal or abbreviated doctor prescription notes using tokenization
    and Levenshtein distance fuzzy matching to map tests into a single-click cart.
    """
    raw_text = req.prescription_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Prescription text cannot be empty")

    all_active_tests = db.query(Test).filter(Test.is_active == True).all()

    # Tokenize input text by common punctuation, line breaks, and conjunctions
    delimiters = r"[,;\n\r\t/&+]|\band\b|\bwith\b|\bplus\b|\balso\b|\badv\b|\bneed\b|\bfor\b"
    raw_tokens = re.split(delimiters, raw_text, flags=re.IGNORECASE)
    cleaned_tokens = [t.strip().lower() for t in raw_tokens if len(t.strip()) > 1]

    matched_tests = []
    matched_test_ids = set()

    for test in all_active_tests:
        best_score = 0.0
        best_match_token = ""
        best_alias = ""
        match_reason = "No Match"

        aliases = CLINICAL_ALIASES.get(test.id, [test.name.lower(), test.id.lower()])

        # 1. Check direct substring matches against full prescription text
        for alias in aliases:
            # Word boundary regex search
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, raw_text, re.IGNORECASE):
                best_score = 1.0
                best_match_token = alias
                best_alias = alias
                match_reason = f"Exact clinical acronym match: '{alias.upper()}'"
                break

        # 2. Check token-level fuzzy matching using Levenshtein distance
        if best_score < 1.0:
            for token in cleaned_tokens:
                for alias in aliases:
                    sim = levenshtein_similarity(token, alias)
                    if sim > best_score and sim >= 0.75:
                        best_score = sim
                        best_match_token = token
                        best_alias = alias
                        match_reason = f"Fuzzy matched '{token}' with '{alias}' (Confidence: {int(sim * 100)}%)"

        if best_score >= 0.75 and test.id not in matched_test_ids:
            matched_test_ids.add(test.id)
            matched_tests.append({
                "id": test.id,
                "name": test.name,
                "category": test.category,
                "price": test.price,
                "sample_type": test.sample_type,
                "tube_cap_class": test.tube_cap_class or "tube-cap-edta",
                "fasting": test.fasting,
                "fasting_hours": test.fasting_hours or 0,
                "confidence": round(best_score, 2),
                "matched_token": best_match_token,
                "matched_alias": best_alias,
                "match_reason": match_reason
            })

    # Sort descending by confidence score
    matched_tests.sort(key=lambda x: x["confidence"], reverse=True)

    total_price = sum(t["price"] for t in matched_tests)
    bundle_discount = round(total_price * 0.10, 2) if len(matched_tests) >= 3 else 0.0
    final_price = total_price - bundle_discount
    requires_fasting = any(t["fasting"] for t in matched_tests)
    max_fasting_hours = max([t["fasting_hours"] for t in matched_tests], default=0)

    fasting_notice = (
        f"Pre-test protocol: {max_fasting_hours} hours overnight water-only fasting is required."
        if requires_fasting
        else "No pre-test fasting required for these investigations."
    )

    return {
        "query_text": raw_text,
        "tokens_analyzed": cleaned_tokens,
        "matched_count": len(matched_tests),
        "matched_tests": matched_tests,
        "total_catalog_price": total_price,
        "bundle_discount": bundle_discount,
        "final_discounted_price": final_price,
        "fasting_required": requires_fasting,
        "max_fasting_hours": max_fasting_hours,
        "fasting_notice": fasting_notice
    }


# ==================== Clinical Association Recommender (Feature 4) ====================

CLINICAL_ASSOCIATIONS: Dict[str, List[Dict[str, Any]]] = {
    "hba1c": [
        {"target_id": "kft", "confidence": 0.84, "reason": "Diabetic Nephropathy & Renal Clearance Monitoring (ADA Protocol)"},
        {"target_id": "lipid", "confidence": 0.78, "reason": "Cardiovascular Risk & Diabetic Dyslipidemia Assessment"}
    ],
    "lipid": [
        {"target_id": "hba1c", "confidence": 0.79, "reason": "Metabolic Syndrome & Insulin Resistance Evaluation"},
        {"target_id": "lft", "confidence": 0.72, "reason": "Baseline Hepatic Enzyme Assessment for Lipid Clearance"}
    ],
    "thyroid": [
        {"target_id": "vitd_b12", "confidence": 0.81, "reason": "Chronic Fatigue, Neuropathy & Autoimmune Screening"},
        {"target_id": "lipid", "confidence": 0.69, "reason": "Hypothyroidism-induced Secondary Hyperlipidemia"}
    ],
    "cbc": [
        {"target_id": "vitd_b12", "confidence": 0.76, "reason": "Megaloblastic Anemia & Peripheral Neuropathy Workup"},
        {"target_id": "lft", "confidence": 0.65, "reason": "Infection & Inflammatory Hepatic Response Tracking"}
    ],
    "lft": [
        {"target_id": "kft", "confidence": 0.83, "reason": "Hepatorenal Function & Metabolic Clearance Index"},
        {"target_id": "lipid", "confidence": 0.74, "reason": "Fatty Liver (NAFLD) & Lipid Clearance Workup"}
    ],
    "kft": [
        {"target_id": "hba1c", "confidence": 0.82, "reason": "Diabetic Kidney Disease Screening"},
        {"target_id": "lft", "confidence": 0.71, "reason": "Comprehensive Metabolic Panel"}
    ],
    "vitd_b12": [
        {"target_id": "thyroid", "confidence": 0.77, "reason": "Endocrine & Cellular Energy Regulation"},
        {"target_id": "cbc", "confidence": 0.75, "reason": "Red Blood Cell Maturation & Hemoglobin Synthesis"}
    ]
}


@router.get("/recommendations")
def get_companion_recommendations(test_ids: str = "", db: Session = Depends(get_db)):
    """
    Computes companion test recommendations using a Clinical Association Matrix
    based on the patient's current cart selection.
    """
    selected_ids = [t.strip().lower() for t in test_ids.split(",") if t.strip()]
    if not selected_ids:
        return {"selected_ids": [], "recommendations": []}

    all_tests = {t.id: t for t in db.query(Test).filter(Test.is_active == True).all()}
    candidate_map: Dict[str, Dict[str, Any]] = {}

    for sel_id in selected_ids:
        assocs = CLINICAL_ASSOCIATIONS.get(sel_id, [])
        for assoc in assocs:
            target_id = assoc["target_id"]
            if target_id in selected_ids:
                continue
            if target_id not in all_tests:
                continue

            target_test = all_tests[target_id]
            conf = assoc["confidence"]
            reason = assoc["reason"]

            if target_id not in candidate_map or conf > candidate_map[target_id]["confidence"]:
                # 15% companion bundle add-on discount
                addon_price = round(target_test.price * 0.85)
                candidate_map[target_id] = {
                    "id": target_test.id,
                    "name": target_test.name,
                    "category": target_test.category,
                    "standard_price": target_test.price,
                    "addon_price": addon_price,
                    "savings": target_test.price - addon_price,
                    "sample_type": target_test.sample_type,
                    "fasting": target_test.fasting,
                    "confidence": conf,
                    "correlation_pct": int(conf * 100),
                    "reason": reason,
                    "triggered_by": sel_id
                }

    recommendations = sorted(candidate_map.values(), key=lambda x: x["confidence"], reverse=True)

    return {
        "selected_ids": selected_ids,
        "recommendation_count": len(recommendations),
        "recommendations": recommendations[:3]
    }




@router.get("", response_model=List[TestOut])
def get_tests(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Test).filter(Test.is_active == True)
    if category:
        query = query.filter(Test.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            (Test.name.ilike(f"%{search}%")) | (Test.description.ilike(f"%{search}%"))
        )
    return query.all()


@router.get("/{test_id}", response_model=TestOut)
def get_test_by_id(test_id: str, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail=f"Test with ID '{test_id}' not found")
    return test


@router.post("", response_model=TestOut, status_code=status.HTTP_201_CREATED)
def create_test(
    test_in: TestCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin))  # Bug 10 fix: admin-only
):
    existing = db.query(Test).filter(Test.id == test_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Test with ID '{test_in.id}' already exists")

    new_test = Test(
        id=test_in.id,
        name=test_in.name,
        category=test_in.category,
        price=test_in.price,
        sample_type=test_in.sample_type,
        tube_cap_class=test_in.tube_cap_class,
        turnaround=test_in.turnaround,
        fasting=test_in.fasting,
        fasting_hours=test_in.fasting_hours,
        description=test_in.description,
        is_active=test_in.is_active,
    )
    db.add(new_test)
    db.flush()

    if test_in.parameters:
        for p in test_in.parameters:
            param = TestParameter(
                test_id=new_test.id,
                key=p.key,
                label=p.label,
                unit=p.unit,
                min_val=p.min_val,
                max_val=p.max_val,
                default_val=p.default_val
            )
            db.add(param)

    db.commit()
    db.refresh(new_test)
    return new_test


@router.put("/{test_id}", response_model=TestOut)
def update_test(
    test_id: str,
    test_update: TestUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin))  # Bug 10 fix: admin-only
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail=f"Test '{test_id}' not found")

    update_data = test_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test, key, value)

    db.commit()
    db.refresh(test)
    return test


@router.delete("/{test_id}", status_code=status.HTTP_200_OK)
def delete_test(
    test_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin))  # Bug 10 fix: admin-only
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail=f"Test '{test_id}' not found")

    # Soft delete
    test.is_active = False
    db.commit()
    return {"message": f"Test '{test_id}' successfully deactivated"}


@router.post("/{test_id}/parameters", response_model=TestParameterOut, status_code=status.HTTP_201_CREATED)
def add_parameter_to_test(
    test_id: str,
    param_in: TestParameterCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin))  # Bug 10 fix: admin-only
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail=f"Test '{test_id}' not found")

    new_param = TestParameter(
        test_id=test_id,
        key=param_in.key,
        label=param_in.label,
        unit=param_in.unit,
        min_val=param_in.min_val,
        max_val=param_in.max_val,
        default_val=param_in.default_val
    )
    db.add(new_param)
    db.commit()
    db.refresh(new_param)
    return new_param
