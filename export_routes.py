import csv
import json
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from .. import models
from ..database import get_db

router = APIRouter(prefix="/export", tags=["export"])


def _asset_rows(db: Session):
    assets = (
        db.query(models.Asset)
        .options(joinedload(models.Asset.category))
        .order_by(models.Asset.id)
        .all()
    )
    rows = []
    for a in assets:
        rows.append(
            {
                "ID": a.id,
                "Name": a.name,
                "Brand": a.brand,
                "Model": a.model_number,
                "Serial": a.serial_number,
                "Category": a.category.name if a.category else "",
                "Status": a.status,
                "Location": a.location,
                "Purchase Date": str(a.purchase_date or ""),
                "Purchase Price": a.purchase_price,
                "Notes": a.notes,
            }
        )
    return rows


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    rows = _asset_rows(db)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys() if rows else [])
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory.csv"},
    )


@router.get("/json")
def export_json(db: Session = Depends(get_db)):
    rows = _asset_rows(db)
    return StreamingResponse(
        iter([json.dumps(rows, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=inventory.json"},
    )
