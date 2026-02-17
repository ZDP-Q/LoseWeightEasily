from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship

# ============================================================================
# Database Models
# ============================================================================


class FoodBase(SQLModel):
    fdc_id: int = Field(primary_key=True)
    food_class: Optional[str] = None
    description: str
    data_type: Optional[str] = None
    ndb_number: Optional[int] = None
    publication_date: Optional[str] = None
    food_category: Optional[str] = None
    scientific_name: Optional[str] = None


class Food(FoodBase, table=True):
    __tablename__ = "foods"
    nutrients: list["FoodNutrient"] = Relationship(
        back_populates="food",
        sa_relationship=relationship("FoodNutrient", back_populates="food")
    )
    portions: list["FoodPortion"] = Relationship(
        back_populates="food",
        sa_relationship=relationship("FoodPortion", back_populates="food")
    )


class NutrientBase(SQLModel):
    nutrient_id: int = Field(primary_key=True)
    nutrient_number: Optional[str] = None
    nutrient_name: Optional[str] = None
    unit_name: Optional[str] = None
    rank: Optional[int] = None


class Nutrient(NutrientBase, table=True):
    __tablename__ = "nutrients"
    food_links: list["FoodNutrient"] = Relationship(
        back_populates="nutrient",
        sa_relationship=relationship("FoodNutrient", back_populates="nutrient")
    )


class FoodNutrientBase(SQLModel):
    fdc_id: int = Field(foreign_key="foods.fdc_id")
    nutrient_id: int = Field(foreign_key="nutrients.nutrient_id")
    amount: Optional[float] = None
    data_points: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    median_value: Optional[float] = None


class FoodNutrient(FoodNutrientBase, table=True):
    __tablename__ = "food_nutrients"
    id: Optional[int] = Field(default=None, primary_key=True)
    food: Food = Relationship(back_populates="nutrients")
    nutrient: Nutrient = Relationship(back_populates="food_links")


class FoodPortionBase(SQLModel):
    id: int = Field(primary_key=True)
    fdc_id: int = Field(foreign_key="foods.fdc_id")
    amount: Optional[float] = None
    measure_unit_name: Optional[str] = None
    measure_unit_abbreviation: Optional[str] = None
    gram_weight: Optional[float] = None
    modifier: Optional[str] = None
    sequence_number: Optional[int] = None


class FoodPortion(FoodPortionBase, table=True):
    __tablename__ = "food_portions"
    food: Food = Relationship(back_populates="portions")


class WeightRecordBase(SQLModel):
    weight_kg: float
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = ""


class WeightRecord(WeightRecordBase, table=True):
    __tablename__ = "weight_records"
    id: Optional[int] = Field(default=None, primary_key=True)


class UserBase(SQLModel):
    name: str
    age: int
    gender: str  # "Male", "Female", "Other"
    height_cm: float
    initial_weight_kg: float
    target_weight_kg: float
    activity_level: Optional[str] = Field(default="sedentary")  # sedentary, light, moderate, active, very_active
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    daily_calorie_goal: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
