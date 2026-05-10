import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.get("/records", response_model=list[schemas.CheckoutRecordOut])
def list_records(active_only: bool = False, db: Session = Depends(get_db)):
    q = db.query(models.CheckoutRecord)
    if active_only:
        q = q.filter(models.CheckoutRecord.returned_at.is_(None))
    return q.order_by(models.CheckoutRecord.checked_out_at.desc()).all()


@router.post("/checkout", status_code=201)
def checkout_asset(data: schemas.CheckoutCreate, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == data.asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    if asset.status != "available":
        raise HTTPException(400, f"Asset is not available (status: {asset.status})")

    record = models.CheckoutRecord(
        asset_id=data.asset_id,
        checked_out_by=data.checked_out_by,
        expected_return_at=data.expected_return_at,
        notes=data.notes,
    )
    asset.status = "checked_out"
    db.add(record)
    db.commit()
    return {"ok": True, "record_id": record.id}


@router.post("/checkin/{record_id}")
def checkin_asset(record_id: int, data: schemas.CheckinUpdate = schemas.CheckinUpdate(), db: Session = Depends(get_db)):
    record = db.query(models.CheckoutRecord).filter(models.CheckoutRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "Checkout record not found")
    if record.returned_at is not None:
        raise HTTPException(400, "Asset already checked in")

    record.returned_at = datetime.datetime.now()
    if data.notes:
        record.notes = (record.notes or "") + f"\n[checkin] {data.notes}"

    asset = db.query(models.Asset).filter(models.Asset.id == record.asset_id).first()
    if asset:
        asset.status = "available"

    db.commit()
    return {"ok": True}
