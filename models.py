import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")

    assets = relationship("Asset", back_populates="category", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100), default="")
    model_number = Column(String(100), default="")
    serial_number = Column(String(100), default="")
    purchase_date = Column(DateTime, nullable=True)
    purchase_price = Column(Float, default=0.0)
    location = Column(String(200), default="")
    status = Column(String(50), default="available")  # available, checked_out, maintenance, retired
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="assets")

    checkout_records = relationship("CheckoutRecord", back_populates="asset", cascade="all, delete-orphan")


class CheckoutRecord(Base):
    __tablename__ = "checkout_records"

    id = Column(Integer, primary_key=True, index=True)
    checked_out_by = Column(String(200), nullable=False)
    checked_out_at = Column(DateTime, default=datetime.datetime.now)
    expected_return_at = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)
    notes = Column(Text, default="")

    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    asset = relationship("Asset", back_populates="checkout_records")
