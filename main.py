import datetime
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from pathlib import Path

from .database import engine, Base, SessionLocal, get_db
from .models import Category, Asset, CheckoutRecord
from .routers import assets, categories, checkout, export_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Company Asset Inventory")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(assets.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(checkout.router, prefix="/api")
app.include_router(export_routes.router)


# ── Page Routes ──

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    db = SessionLocal()
    try:
        total_assets = db.query(func.count(Asset.id)).scalar() or 0
        total_categories = db.query(func.count(Category.id)).scalar() or 0
        available = db.query(func.count(Asset.id)).filter(Asset.status == "available").scalar() or 0
        checked_out = db.query(func.count(Asset.id)).filter(Asset.status == "checked_out").scalar() or 0
        maintenance = db.query(func.count(Asset.id)).filter(Asset.status == "maintenance").scalar() or 0
        recent_assets = db.query(Asset).options(joinedload(Asset.category)).order_by(Asset.created_at.desc()).limit(5).all()
        cats = db.query(Category).all()
        category_stats = [
            {"name": cat.name, "count": db.query(func.count(Asset.id)).filter(Asset.category_id == cat.id).scalar() or 0}
            for cat in cats
        ]
    finally:
        db.close()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "total_assets": total_assets, "total_categories": total_categories,
        "available": available, "checked_out": checked_out, "maintenance": maintenance,
        "recent_assets": recent_assets, "category_stats": category_stats,
    })


@app.get("/assets", response_class=HTMLResponse, include_in_schema=False)
def assets_page(request: Request, search: str = "", category_id: str = "", status: str = ""):
    db = SessionLocal()
    try:
        cat_id = int(category_id) if category_id.isdigit() else 0
        q = db.query(Asset).options(joinedload(Asset.category))
        if search:
            like = f"%{search}%"
            from sqlalchemy import or_
            q = q.filter(or_(Asset.name.ilike(like), Asset.brand.ilike(like), Asset.model_number.ilike(like), Asset.serial_number.ilike(like), Asset.location.ilike(like)))
        if cat_id:
            q = q.filter(Asset.category_id == cat_id)
        if status:
            q = q.filter(Asset.status == status)
        assets_list = q.order_by(Asset.created_at.desc()).all()
        enriched = []
        for a in assets_list:
            o = {
                "id": a.id, "name": a.name, "brand": a.brand, "model_number": a.model_number,
                "serial_number": a.serial_number, "location": a.location, "status": a.status,
                "category_name": a.category.name if a.category else "", "category_id": a.category_id,
            }
            enriched.append(o)
        cats = db.query(Category).all()
    finally:
        db.close()
    return templates.TemplateResponse("assets_list.html", {
        "request": request, "assets": enriched, "categories": cats,
        "search": search, "category_id": category_id, "status": status,
    })


@app.get("/assets/new", response_class=HTMLResponse, include_in_schema=False)
def new_asset_page(request: Request, category_id: str = ""):
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
    finally:
        db.close()
    selected = int(category_id) if category_id.isdigit() else 0
    return templates.TemplateResponse("asset_form.html", {
        "request": request, "asset": None, "categories": cats, "selected_category": selected,
    })


@app.post("/assets/new")
def create_asset_page(
    request: Request,
    name: str = Form(...), brand: str = Form(""), model_number: str = Form(""),
    serial_number: str = Form(""), category_id: int = Form(...), status: str = Form("available"),
    location: str = Form(""), purchase_date: str = Form(""), purchase_price: float = Form(0.0),
    notes: str = Form(""),
):
    db = SessionLocal()
    try:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            db.close()
            return RedirectResponse("/assets/new", status_code=303)
        pd = None
        if purchase_date:
            try:
                pd = datetime.date.fromisoformat(purchase_date)
            except ValueError:
                pass
        asset = Asset(name=name, brand=brand, model_number=model_number, serial_number=serial_number,
                      category_id=category_id, status=status, location=location,
                      purchase_date=pd, purchase_price=purchase_price, notes=notes)
        db.add(asset)
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/assets", status_code=303)


@app.get("/assets/{asset_id}", response_class=HTMLResponse, include_in_schema=False)
def asset_detail_page(request: Request, asset_id: int):
    db = SessionLocal()
    try:
        asset = db.query(Asset).options(joinedload(Asset.category), joinedload(Asset.checkout_records)).filter(Asset.id == asset_id).first()
        if not asset:
            return RedirectResponse("/assets", status_code=303)
    finally:
        db.close()
    return templates.TemplateResponse("asset_detail.html", {"request": request, "asset": asset})


@app.get("/assets/{asset_id}/edit", response_class=HTMLResponse, include_in_schema=False)
def edit_asset_page(request: Request, asset_id: int):
    db = SessionLocal()
    try:
        asset = db.query(Asset).options(joinedload(Asset.category)).filter(Asset.id == asset_id).first()
        cats = db.query(Category).all()
        if not asset:
            return RedirectResponse("/assets", status_code=303)
    finally:
        db.close()
    return templates.TemplateResponse("asset_form.html", {"request": request, "asset": asset, "categories": cats, "selected_category": asset.category_id})


@app.post("/assets/{asset_id}/edit")
def update_asset_page(
    request: Request, asset_id: int,
    name: str = Form(...), brand: str = Form(""), model_number: str = Form(""),
    serial_number: str = Form(""), category_id: int = Form(...), status: str = Form("available"),
    location: str = Form(""), purchase_date: str = Form(""), purchase_price: float = Form(0.0),
    notes: str = Form(""),
):
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return RedirectResponse("/assets", status_code=303)
        pd = None
        if purchase_date:
            try:
                pd = datetime.date.fromisoformat(purchase_date)
            except ValueError:
                pd = asset.purchase_date
        asset.name = name
        asset.brand = brand
        asset.model_number = model_number
        asset.serial_number = serial_number
        asset.category_id = category_id
        asset.status = status
        asset.location = location
        asset.purchase_date = pd
        asset.purchase_price = purchase_price
        asset.notes = notes
        asset.updated_at = datetime.datetime.now()
        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/assets/{asset_id}", status_code=303)


@app.post("/api/assets/{asset_id}/delete")
def delete_asset_page(asset_id: int):
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            db.delete(asset)
            db.commit()
    finally:
        db.close()
    return RedirectResponse("/assets", status_code=303)


@app.get("/categories", response_class=HTMLResponse, include_in_schema=False)
def categories_page(request: Request):
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
        result = []
        for c in cats:
            cnt = db.query(func.count(Asset.id)).filter(Asset.category_id == c.id).scalar() or 0
            result.append({"id": c.id, "name": c.name, "description": c.description, "asset_count": cnt})
    finally:
        db.close()
    return templates.TemplateResponse("categories.html", {"request": request, "categories": result})


@app.post("/categories")
def create_category_page(name: str = Form(...), description: str = Form("")):
    db = SessionLocal()
    try:
        existing = db.query(Category).filter(Category.name == name).first()
        if not existing:
            db.add(Category(name=name, description=description))
            db.commit()
    finally:
        db.close()
    return RedirectResponse("/categories", status_code=303)


@app.post("/api/categories/{category_id}/delete")
def delete_category_page(category_id: int):
    db = SessionLocal()
    try:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if cat:
            db.delete(cat)
            db.commit()
    finally:
        db.close()
    return RedirectResponse("/categories", status_code=303)


@app.get("/checkout", response_class=HTMLResponse, include_in_schema=False)
def checkout_page(request: Request, active_only: bool = False):
    db = SessionLocal()
    try:
        q = db.query(CheckoutRecord).options(joinedload(CheckoutRecord.asset))
        if active_only:
            q = q.filter(CheckoutRecord.returned_at.is_(None))
        records = q.order_by(CheckoutRecord.checked_out_at.desc()).all()
    finally:
        db.close()
    return templates.TemplateResponse("checkout.html", {"request": request, "records": records, "active_only": active_only})


@app.post("/api/checkout")
def checkout_form(asset_id: int = Form(...), checked_out_by: str = Form(...),
                  expected_return_at: str = Form(""), notes: str = Form("")):
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset or asset.status != "available":
            return RedirectResponse(f"/assets/{asset_id}", status_code=303)
        era = None
        if expected_return_at:
            try:
                era = datetime.datetime.fromisoformat(expected_return_at)
            except ValueError:
                pass
        record = CheckoutRecord(asset_id=asset_id, checked_out_by=checked_out_by,
                                expected_return_at=era, notes=notes)
        asset.status = "checked_out"
        db.add(record)
        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/assets/{asset_id}", status_code=303)


@app.post("/api/checkin/{record_id}")
def checkin_form(record_id: int):
    db = SessionLocal()
    try:
        record = db.query(CheckoutRecord).filter(CheckoutRecord.id == record_id).first()
        if record and record.returned_at is None:
            record.returned_at = datetime.datetime.now()
            asset = db.query(Asset).filter(Asset.id == record.asset_id).first()
            if asset:
                asset.status = "available"
            db.commit()
    finally:
        db.close()
    return RedirectResponse("/checkout", status_code=303)
