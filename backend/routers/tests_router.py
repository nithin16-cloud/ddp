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
    "cbc": ["cbc", "complete blood count", "hemogram", "complete hemogram", "blood count", "hb", "hemoglobin", "platelets", "platelet count", "wbc", "rbc", "pcv", "blood routine", "blood examination"],
    "lipid": ["lipid", "lipid profile", "cholesterol", "chol", "triglycerides", "tg", "hdl", "ldl", "vldl", "cardiac lipid", "lipid panel", "serum lipids", "dyslipidemia"],
    "thyroid": ["thyroid", "tft", "tsh", "thyroid profile", "t3", "t4", "ultrasensitive tsh", "thyroid test", "thyroid panel", "t3 t4 tsh"],
    "hba1c": ["hba1c", "glycated hemoglobin", "estimated glucose", "eag", "glycohemoglobin", "a1c", "diabetes panel", "hba1c test", "3 month sugar"],
    "lft": ["lft", "liver function", "liver function test", "sgot", "sgpt", "alt", "ast", "bilirubin", "bili", "liver enzymes", "hepatic", "liver profile", "hepatic panel", "alkaline phosphatase"],
    "kft": ["kft", "kidney function", "kidney function test", "creatinine", "sr creatinine", "serum creatinine", "urea", "bun", "uric acid", "renal profile", "renal panel", "kidney panel", "rft"],
    "vitd_b12": ["vitamin d", "vit d", "vitamin b12", "vit b12", "b12", "d3", "cholecalciferol", "cyanocobalamin", "vitality duo", "vitamin d3", "vit d3", "b12 deficiency"],
    "fbs_ppbs": ["fbs", "ppbs", "fasting blood sugar", "post prandial blood sugar", "blood sugar fasting", "pp sugar", "glucose fasting", "fbs ppbs", "fasting glucose", "pp glucose", "blood sugar", "sugar test", "rbs", "random blood sugar", "fasting and pp", "fasting sugar", "ppbs test"],
    "crp": ["crp", "c reactive protein", "hs crp", "hscrp", "c-reactive protein", "inflammation marker", "quantitative crp", "reactive protein", "high sensitivity crp", "crp quantitative", "cardiac crp"],
    "urine_re": ["urine routine", "urine r/e", "urinalysis", "urine re", "urine microscopy", "cue", "complete urine exam", "urine culture screen", "urine test", "urine rm", "routine urine", "urine r/m", "urine analysis"],
    "electrolytes": ["electrolytes", "serum electrolytes", "lytes", "na k cl", "sodium potassium", "sodium", "potassium", "electrolyte panel", "serum sodium", "serum potassium", "iono", "serum ions"],
    "esr": ["esr", "erythrocyte sedimentation rate", "sed rate", "sedimentation rate", "westergren esr", "esr 1st hour", "sedrate", "westergren", "sed rate westergren"],
    "iron_profile": ["iron profile", "serum ferritin", "ferritin", "iron", "serum iron", "tibc", "transferrin", "iron studies", "iron panel", "fe profile", "iron deficiency", "anemia profile", "anemia panel"],
    "dengue": ["dengue", "dengue ns1", "dengue serology", "dengue profile", "ns1 antigen", "dengue igm", "dengue duo", "dengue test", "breakbone", "dengue fever", "ns1 igm igg", "dengue antibody"],
    "typhoid": ["typhoid", "widal", "widal test", "typhidot", "enteric fever", "salmonella typhi", "typhoid serology", "widal slide test", "typhi dot", "enteric fever panel"],
    "troponin": ["troponin", "trop i", "troponin i", "hs-ctni", "hstroponin", "cardiac troponin", "trop-i", "cardiac enzymes", "heart attack marker", "ctni", "troponin t", "hs trop", "myocardial marker"],
    "coagulation": ["coagulation", "pt", "inr", "pt/inr", "prothrombin time", "aptt", "clotting profile", "coagulation profile", "bleeding time", "pt inr", "clotting time", "inr test", "pre op coagulation"],
    "calcium_phosphorus": ["calcium", "serum calcium", "phosphorus", "calcium phosphorus", "bone mineral", "ionized calcium", "ca++", "hypocalcemia", "hypercalcemia", "total calcium", "bone profile"],
    "pancreatic": ["amylase", "lipase", "pancreatic", "pancreas", "serum lipase", "serum amylase", "pancreatic enzymes", "acute pancreatitis", "pancreas panel", "amylase lipase"],
    "urine_microalbumin": ["microalbumin", "urine microalbumin", "acr", "albumin creatinine ratio", "urine acr", "spot microalbumin", "diabetic kidney screen", "renal microalbumin", "microalbuminuria", "urine albumin"],
    "psa": ["psa", "prostate specific antigen", "total psa", "prostate test", "psa screening", "prostate antigen", "serum psa", "psa total", "prostate screen"],
    "rheumatoid": ["rheumatoid", "rf", "ra factor", "rheumatoid factor", "anti ccp", "anticcp", "arthritis", "joint pain panel", "rheumatoid arthritis", "ra test", "arthritis panel", "ra factor quantitative"],
    "uric_acid": ["uric acid", "serum uric acid", "gout", "hyperuricemia", "urate", "gout test", "uric", "uric acid level", "blood uric acid"],
    "viral_screen": ["viral marker", "viral markers", "hiv", "hbsag", "hcv", "hepatitis b", "hepatitis c", "pre op viral screen", "viral screening", "serology tri panel", "australia antigen", "hiv hbsag hcv", "tri dot"],
    "cardiac_risk": ["cardiac risk", "homocysteine", "apolipoprotein", "apo b", "lp a", "lipoprotein a", "advanced cardiac", "heart risk", "vascular risk", "atherosclerosis panel", "apo-b"],
    "allergy_ige": ["ige", "total ige", "allergy", "allergy test", "immunoglobulin e", "atopy", "allergic rhinitis", "asthma panel", "allergy screen", "serum ige", "allergy profile"],
    "beta_hcg": ["hcg", "beta hcg", "b-hcg", "pregnancy test", "pregnancy blood test", "human chorionic gonadotropin", "bhcg", "beta-hcg", "serum beta hcg", "serum pregnancy test"]
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

    # Tokenize input text by common punctuation, line breaks, and clinical conjunctions
    delimiters = r"[,;\n\r\t/&+]|\band\b|\bwith\b|\bplus\b|\balso\b|\badv\b|\badvise\b|\brx\b|\bcheck\b|\btest\b|\btests\b|\bpanel\b|\bneed\b|\bfor\b"
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
        {"target_id": "lipid", "confidence": 0.78, "reason": "Cardiovascular Risk & Diabetic Dyslipidemia Assessment"},
        {"target_id": "urine_microalbumin", "confidence": 0.88, "reason": "Early Microvascular Diabetic Nephropathy Detection"}
    ],
    "fbs_ppbs": [
        {"target_id": "hba1c", "confidence": 0.94, "reason": "Glycated Hemoglobin 90-Day Glycemic Control Correlation"},
        {"target_id": "urine_microalbumin", "confidence": 0.86, "reason": "Glomerular Hyperfiltration & Diabetic Renal Screening"}
    ],
    "lipid": [
        {"target_id": "hba1c", "confidence": 0.79, "reason": "Metabolic Syndrome & Insulin Resistance Evaluation"},
        {"target_id": "lft", "confidence": 0.72, "reason": "Baseline Hepatic Enzyme Assessment for Lipid Clearance"},
        {"target_id": "cardiac_risk", "confidence": 0.83, "reason": "Apolipoprotein-B & Vascular Endothelial Risk Assessment"}
    ],
    "troponin": [
        {"target_id": "lipid", "confidence": 0.86, "reason": "Atherosclerotic Coronary Plaque Risk Assessment"},
        {"target_id": "electrolytes", "confidence": 0.82, "reason": "Arrhythmogenic Myocardial Ion Surveillance (K+/Mg2+)"},
        {"target_id": "crp", "confidence": 0.80, "reason": "Acute Coronary Arterial Wall Inflammation Index"}
    ],
    "crp": [
        {"target_id": "cbc", "confidence": 0.88, "reason": "Leukocyte & Platelet Infection Response Differential"},
        {"target_id": "esr", "confidence": 0.85, "reason": "Synchronous Acute vs Chronic Inflammatory Phase Tracking"}
    ],
    "esr": [
        {"target_id": "cbc", "confidence": 0.89, "reason": "Anemia & White Cell Differential Correlation"},
        {"target_id": "crp", "confidence": 0.84, "reason": "Complementary Acute-Phase Protein Confirmation"}
    ],
    "dengue": [
        {"target_id": "cbc", "confidence": 0.96, "reason": "Urgent Platelet Count & Hemoconcentration (PCV) Surveillance"},
        {"target_id": "lft", "confidence": 0.78, "reason": "Hepatic Transaminase Flare Monitoring in Dengue"}
    ],
    "typhoid": [
        {"target_id": "cbc", "confidence": 0.86, "reason": "Relative Bradycardia & Leukopenia Differential in Pyrexia"},
        {"target_id": "lft", "confidence": 0.77, "reason": "Enteric Hepatitis & Hepatic Clearance Monitoring"}
    ],
    "thyroid": [
        {"target_id": "vitd_b12", "confidence": 0.81, "reason": "Chronic Fatigue, Neuropathy & Autoimmune Screening"},
        {"target_id": "lipid", "confidence": 0.69, "reason": "Hypothyroidism-induced Secondary Hyperlipidemia"}
    ],
    "cbc": [
        {"target_id": "esr", "confidence": 0.88, "reason": "Systemic Inflammatory & Infection Severity Index"},
        {"target_id": "iron_profile", "confidence": 0.86, "reason": "Iron Deficiency Microcytic Anemia Differential"},
        {"target_id": "vitd_b12", "confidence": 0.76, "reason": "Megaloblastic Anemia & Cellular Maturation Workup"}
    ],
    "lft": [
        {"target_id": "kft", "confidence": 0.83, "reason": "Hepatorenal Function & Metabolic Clearance Index"},
        {"target_id": "lipid", "confidence": 0.74, "reason": "Fatty Liver (NAFLD) & Lipid Clearance Workup"},
        {"target_id": "viral_screen", "confidence": 0.79, "reason": "Viral Hepatitis (HBsAg / HCV) Etiology Screen"}
    ],
    "kft": [
        {"target_id": "electrolytes", "confidence": 0.89, "reason": "Renal Tubular Excretion & Electrolyte Clearance Index"},
        {"target_id": "urine_re", "confidence": 0.84, "reason": "Complete Urinary Sediment & Proteinuria Correlation"},
        {"target_id": "hba1c", "confidence": 0.82, "reason": "Diabetic Kidney Disease Screening"}
    ],
    "electrolytes": [
        {"target_id": "kft", "confidence": 0.89, "reason": "Renal Glomerular & Tubular Filtration Balance"},
        {"target_id": "calcium_phosphorus", "confidence": 0.78, "reason": "Complete Mineral & Divalent Cation Homeostasis"}
    ],
    "urine_re": [
        {"target_id": "kft", "confidence": 0.83, "reason": "Glomerular Clearance & Creatinine Evaluation"},
        {"target_id": "urine_microalbumin", "confidence": 0.80, "reason": "Early Quantitative Microalbuminuria Confirmation"}
    ],
    "iron_profile": [
        {"target_id": "cbc", "confidence": 0.92, "reason": "Complete Red Blood Cell Indices & Hematocrit Correlation"},
        {"target_id": "vitd_b12", "confidence": 0.80, "reason": "Nutritional Anemia & Co-Factor Deficiency Workup"}
    ],
    "rheumatoid": [
        {"target_id": "crp", "confidence": 0.89, "reason": "Synovial Inflammation Severity & Disease Activity Score"},
        {"target_id": "uric_acid", "confidence": 0.83, "reason": "Gouty vs Rheumatoid Polyarthritis Differential"},
        {"target_id": "esr", "confidence": 0.81, "reason": "Chronic Autoimmune Flare-up Rate Tracking"}
    ],
    "uric_acid": [
        {"target_id": "kft", "confidence": 0.86, "reason": "Renal Urate Clearance & Gout Nephropathy Assessment"},
        {"target_id": "lipid", "confidence": 0.73, "reason": "Metabolic Syndrome & Hyperuricemia Co-Morbidity"}
    ],
    "pancreatic": [
        {"target_id": "lft", "confidence": 0.85, "reason": "Biliary Gallstone Pancreatitis & Obstruction Workup"},
        {"target_id": "electrolytes", "confidence": 0.80, "reason": "Pancreatic Third-Spacing Fluid & Electrolyte Shift"}
    ],
    "calcium_phosphorus": [
        {"target_id": "vitd_b12", "confidence": 0.90, "reason": "Vitamin D-Dependent Calcium Absorption & Bone Health"},
        {"target_id": "kft", "confidence": 0.79, "reason": "Renal Calcium/Phosphate Excretion Dynamics"}
    ],
    "psa": [
        {"target_id": "urine_re", "confidence": 0.82, "reason": "Exclude Urinary Infection Artifact in Elevated PSA"},
        {"target_id": "kft", "confidence": 0.75, "reason": "Obstructive Uropathy & Renal Outflow Surveillance"}
    ],
    "coagulation": [
        {"target_id": "cbc", "confidence": 0.88, "reason": "Baseline Platelet Count for Primary Hemostasis"},
        {"target_id": "lft", "confidence": 0.85, "reason": "Hepatic Synthesis of Vitamin K Clotting Factors"}
    ],
    "viral_screen": [
        {"target_id": "lft", "confidence": 0.87, "reason": "Hepatocellular Damage & Transaminase Baseline"},
        {"target_id": "cbc", "confidence": 0.78, "reason": "Immunologic Lymphocyte & Cytopenia Screening"}
    ],
    "allergy_ige": [
        {"target_id": "cbc", "confidence": 0.87, "reason": "Absolute Eosinophil Count (AEC) Allergic Correlation"}
    ],
    "cardiac_risk": [
        {"target_id": "lipid", "confidence": 0.91, "reason": "Primary Lipid Profile Atherogenic Subfraction Baseline"},
        {"target_id": "troponin", "confidence": 0.82, "reason": "Subclinical Myocardial Stress & Troponin Baseline"}
    ],
    "urine_microalbumin": [
        {"target_id": "hba1c", "confidence": 0.90, "reason": "Diabetic Microvascular Complication Monitoring"},
        {"target_id": "kft", "confidence": 0.85, "reason": "Renal Clearance & Glomerular Filtration Integrity"}
    ],
    "vitd_b12": [
        {"target_id": "thyroid", "confidence": 0.77, "reason": "Endocrine & Cellular Energy Regulation"},
        {"target_id": "cbc", "confidence": 0.75, "reason": "Red Blood Cell Maturation & Hemoglobin Synthesis"},
        {"target_id": "calcium_phosphorus", "confidence": 0.88, "reason": "Cholecalciferol-Bone Mineralization Homeostasis"}
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
    tests = query.all()
    # Prioritize Complete Blood Count (CBC) at the top of the test catalog
    tests.sort(key=lambda t: 0 if t.id == "cbc" or "complete blood count" in (t.name or "").lower() else 1)
    return tests


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
