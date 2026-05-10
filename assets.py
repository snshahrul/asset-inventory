import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/assets", tags=["assets"])


def _enrich_asset(asset: models.Asset) -> schemas.AssetOut:
    out = schemas.AssetOut.model_validate(asset)
    out.category_name = asset.category.name if asset.category else ""
    return out


@router.get("/", response_model=list[schemas.AssetOut])
def list_assets(
    search: str = "",
    category_id: int = 0,
    status: str = "",
    db: Session = Depends(get_db),
):
    q = db.query(models.Asset).options(joinedload(models.Asset.category), joinedload(models.Asset.checkout_records))
    if search:
        like = f"%{search}%"
        q = q.filter(
            or_(
                models.Asset.name.ilike(like),
                models.Asset.brand.ilike(like),
                models.Asset.model_number.ilike(like),
                models.Asset.serial_number.ilike(like),
                models.Asset.location.ilike(like),
            )
        )
    if category_id:
        q = q.filter(models.Asset.category_id == category_id)
    if status:
        q = q.filter(models.Asset.status == status)
    return [_enrich_asset(a) for a in q.all()]


@router.get("/{asset_id}", response_model=schemas.AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = (
        db.query(models.Asset)
        .options(joinedload(models.Asset.category), joinedload(models.Asset.checkout_records))
        .filter(models.Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(404, "Asset not found")
    return _enrich_asset(asset)


@router.post("/", response_model=schemas.AssetOut, status_code=201)
def create_asset(data: schemas.AssetCreate, db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(400, "Category not found")
    asset = models.Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _enrich_asset(asset)


@router.put("/{asset_id}", response_model=schemas.AssetOut)
def update_asset(asset_id: int, data: schemas.AssetUpdate, db: Session = Depends(get_db)):
    asset = (
        db.query(models.Asset)
        .options(joinedload(models.Asset.category))
        .filter(models.Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(404, "Asset not found")
    update_data = data.model_dump(exclude_unset=True)
    if "category_id" in update_data and update_data["category_id"] is not None:
        cat = db.query(models.Category).filter(models.Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(400, "Category not found")
    for key, val in update_data.items():
        setattr(asset, key, val)
    asset.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(asset)
    return _enrich_asset(asset)


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    db.delete(asset)
    db.commit()
    return {"ok": True}
