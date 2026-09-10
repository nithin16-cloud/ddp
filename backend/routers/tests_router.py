from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Test, TestParameter, User, UserRole
from schemas import TestCreate, TestUpdate, TestOut, TestParameterCreate, TestParameterOut
from dependencies import require_role

router = APIRouter(prefix="/tests", tags=["Tests Catalog"])


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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
def delete_test(test_id: str, db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)
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
