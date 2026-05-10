import datetime
from pydantic import BaseModel, Field
from typing import Optional


# ── Category ──
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = ""


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int
    asset_count: int = 0

    class Config:
        from_attributes = True


# ── Asset ──
class AssetBase(BaseModel):
    name: str = Field(..., max_length=200)
    brand: str = ""
    model_number: str = ""
    serial_number: str = ""
    purchase_date: Optional[datetime.date] = None
    purchase_price: float = 0.0
    location: str = ""
    status: str = "available"
    notes: str = ""
    category_id: int


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime.date] = None
    purchase_price: Optional[float] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    category_id: Optional[int] = None


class CheckoutRecordOut(BaseModel):
    id: int
    checked_out_by: str
    checked_out_at: datetime.datetime
    expected_return_at: Optional[datetime.datetime] = None
    returned_at: Optional[datetime.datetime] = None
    notes: str

    class Config:
        from_attributes = True


class AssetOut(AssetBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    category_name: str = ""
    checkout_records: list[CheckoutRecordOut] = []

    class Config:
        from_attributes = True


# ── Checkout ──
class CheckoutCreate(BaseModel):
    asset_id: int
    checked_out_by: str = Field(..., max_length=200)
    expected_return_at: Optional[datetime.datetime] = None
    notes: str = ""


class CheckinUpdate(BaseModel):
    notes: str = ""
