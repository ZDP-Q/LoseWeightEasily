import json
import logging
from pathlib import Path
from sqlmodel import Session, create_engine, select
from core.config import get_settings
from models import Food, Nutrient, FoodNutrient, FoodPortion

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_data():
    settings = get_settings()
    engine = create_engine(str(settings.database.url))

    json_path = Path("data/FoodData_Central_foundation_food_json_2025-12-18.json")
    if not json_path.exists():
        logger.error(f"File not found: {json_path}")
        return

    logger.info(f"Loading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    foundation_foods = data.get("FoundationFoods", [])
    logger.info(f"Found {len(foundation_foods)} foods to import.")

    with Session(engine) as session:
        for i, food_data in enumerate(foundation_foods):
            fdc_id = food_data.get("fdcId")

            # 1. Create or update Food
            food = session.get(Food, fdc_id)
            if not food:
                food_category = food_data.get("foodCategory")
                if isinstance(food_category, dict):
                    food_category = food_category.get("description")

                food = Food(
                    fdc_id=fdc_id,
                    food_class=food_data.get("foodClass"),
                    description=food_data.get("description"),
                    data_type=food_data.get("dataType"),
                    ndb_number=food_data.get("ndbNumber"),
                    publication_date=food_data.get("publicationDate"),
                    food_category=food_category,
                )
                session.add(food)

            # 2. Process Nutrients
            for fn_data in food_data.get("foodNutrients", []):
                n_data = fn_data.get("nutrient", {})
                nutrient_id = n_data.get("id")

                if not nutrient_id:
                    continue

                nutrient = session.get(Nutrient, nutrient_id)
                if not nutrient:
                    nutrient = Nutrient(
                        nutrient_id=nutrient_id,
                        nutrient_number=n_data.get("number"),
                        nutrient_name=n_data.get("name"),
                        unit_name=n_data.get("unitName"),
                        rank=n_data.get("rank"),
                    )
                    session.add(nutrient)
                    session.flush()  # Ensure nutrient is available for FoodNutrient

                # Link Food and Nutrient
                # Check if link already exists
                statement = select(FoodNutrient).where(
                    FoodNutrient.fdc_id == fdc_id,
                    FoodNutrient.nutrient_id == nutrient_id,
                )
                fn_link = session.exec(statement).first()
                if not fn_link:
                    fn_link = FoodNutrient(
                        fdc_id=fdc_id,
                        nutrient_id=nutrient_id,
                        amount=fn_data.get("amount"),
                        data_points=fn_data.get("dataPoints"),
                        min_value=fn_data.get("min"),
                        max_value=fn_data.get("max"),
                        median_value=fn_data.get("median"),
                    )
                    session.add(fn_link)

            # 3. Process Portions
            for fp_data in food_data.get("foodPortions", []):
                portion_id = fp_data.get("id")
                portion = session.get(FoodPortion, portion_id)
                if not portion:
                    measure_unit = fp_data.get("measureUnit", {})
                    portion = FoodPortion(
                        id=portion_id,
                        fdc_id=fdc_id,
                        amount=fp_data.get("amount"),
                        measure_unit_name=measure_unit.get("name"),
                        measure_unit_abbreviation=measure_unit.get("abbreviation"),
                        gram_weight=fp_data.get("gramWeight"),
                        modifier=fp_data.get("modifier"),
                        sequence_number=fp_data.get("sequenceNumber"),
                    )
                    session.add(portion)

            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(foundation_foods)} foods...")
                session.commit()

        session.commit()
        logger.info("Import completed successfully.")


if __name__ == "__main__":
    import_data()
