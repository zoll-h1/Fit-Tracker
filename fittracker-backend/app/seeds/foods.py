"""Seed 200 common foods into foods table.
Run: python -m app.seeds.foods
"""
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

# Each entry: (name, calories_per_100g, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg)
FOODS = [
    # PROTEINS - Meat & Poultry
    ("Chicken Breast (cooked)", 165, 31.0, 0.0, 3.6, 0.0, 0.0, 74),
    ("Chicken Thigh (cooked)", 209, 26.0, 0.0, 11.0, 0.0, 0.0, 84),
    ("Turkey Breast (cooked)", 135, 30.0, 0.0, 1.0, 0.0, 0.0, 63),
    ("Ground Beef 80/20 (cooked)", 254, 26.0, 0.0, 17.0, 0.0, 0.0, 75),
    ("Ground Beef 93/7 (cooked)", 218, 27.0, 0.0, 12.0, 0.0, 0.0, 80),
    ("Beef Steak (ribeye)", 291, 24.0, 0.0, 21.0, 0.0, 0.0, 65),
    ("Beef Steak (sirloin)", 207, 26.0, 0.0, 11.0, 0.0, 0.0, 60),
    ("Pork Tenderloin (cooked)", 143, 26.0, 0.0, 3.5, 0.0, 0.0, 62),
    ("Bacon (cooked)", 541, 37.0, 0.6, 42.0, 0.0, 0.0, 1717),
    ("Ham (deli)", 113, 16.0, 1.5, 5.0, 0.0, 1.2, 1203),
    ("Lamb Chop (cooked)", 258, 26.0, 0.0, 17.0, 0.0, 0.0, 72),
    ("Venison (cooked)", 158, 30.0, 0.0, 3.2, 0.0, 0.0, 60),
    # PROTEINS - Seafood
    ("Salmon (Atlantic, cooked)", 206, 28.0, 0.0, 10.0, 0.0, 0.0, 59),
    ("Tuna (canned in water)", 116, 26.0, 0.0, 1.0, 0.0, 0.0, 337),
    ("Shrimp (cooked)", 99, 24.0, 0.0, 0.3, 0.0, 0.0, 224),
    ("Tilapia (cooked)", 128, 26.0, 0.0, 2.7, 0.0, 0.0, 56),
    ("Cod (cooked)", 105, 23.0, 0.0, 0.9, 0.0, 0.0, 78),
    ("Sardines (canned)", 208, 25.0, 0.0, 11.0, 0.0, 0.0, 505),
    ("Mackerel (cooked)", 262, 24.0, 0.0, 18.0, 0.0, 0.0, 83),
    ("Crab (cooked)", 97, 19.0, 0.0, 1.8, 0.0, 0.0, 912),
    # PROTEINS - Eggs & Dairy
    ("Whole Egg", 155, 13.0, 1.1, 11.0, 0.0, 1.1, 124),
    ("Egg White", 52, 11.0, 0.7, 0.2, 0.0, 0.6, 166),
    ("Greek Yogurt (plain, 0% fat)", 59, 10.0, 3.6, 0.4, 0.0, 3.6, 36),
    ("Greek Yogurt (plain, 2% fat)", 73, 9.0, 4.0, 2.0, 0.0, 4.0, 44),
    ("Cottage Cheese (1% fat)", 72, 12.0, 2.7, 1.0, 0.0, 2.7, 406),
    ("Whole Milk", 61, 3.2, 4.8, 3.3, 0.0, 5.0, 44),
    ("Skim Milk", 34, 3.4, 5.0, 0.2, 0.0, 5.0, 44),
    ("Cheddar Cheese", 402, 25.0, 1.3, 33.0, 0.0, 0.5, 621),
    ("Mozzarella Cheese", 280, 28.0, 2.2, 17.0, 0.0, 1.0, 486),
    ("Whey Protein Powder", 380, 75.0, 8.0, 5.0, 0.0, 4.0, 100),
    # CARBS - Grains & Bread
    ("White Rice (cooked)", 130, 2.7, 28.0, 0.3, 0.4, 0.0, 1),
    ("Brown Rice (cooked)", 112, 2.6, 24.0, 0.8, 1.8, 0.0, 5),
    ("Oatmeal (cooked)", 71, 2.5, 12.0, 1.5, 1.7, 0.0, 49),
    ("Rolled Oats (dry)", 379, 13.0, 68.0, 7.0, 10.0, 1.0, 6),
    ("Whole Wheat Bread", 247, 13.0, 41.0, 4.2, 7.0, 6.0, 400),
    ("White Bread", 265, 9.0, 49.0, 3.2, 2.7, 5.0, 491),
    ("Pasta (cooked)", 158, 5.8, 31.0, 0.9, 1.8, 0.6, 1),
    ("Whole Wheat Pasta (cooked)", 174, 7.5, 37.0, 0.8, 4.5, 0.5, 4),
    ("Quinoa (cooked)", 120, 4.4, 22.0, 1.9, 2.8, 0.9, 7),
    ("Couscous (cooked)", 112, 3.8, 23.0, 0.2, 1.4, 0.1, 5),
    ("Bagel (plain)", 245, 9.8, 47.0, 1.5, 1.9, 5.5, 440),
    ("Tortilla (flour)", 308, 8.0, 51.0, 8.0, 3.3, 2.5, 589),
    ("Corn Tortilla", 218, 5.7, 46.0, 2.8, 6.3, 0.7, 18),
    # CARBS - Fruits
    ("Banana", 89, 1.1, 23.0, 0.3, 2.6, 12.0, 1),
    ("Apple", 52, 0.3, 14.0, 0.2, 2.4, 10.0, 1),
    ("Orange", 47, 0.9, 12.0, 0.1, 2.4, 9.4, 0),
    ("Blueberries", 57, 0.7, 14.0, 0.3, 2.4, 10.0, 1),
    ("Strawberries", 32, 0.7, 7.7, 0.3, 2.0, 4.9, 1),
    ("Mango", 60, 0.8, 15.0, 0.4, 1.6, 14.0, 1),
    ("Pineapple", 50, 0.5, 13.0, 0.1, 1.4, 9.9, 1),
    ("Watermelon", 30, 0.6, 7.6, 0.2, 0.4, 6.2, 1),
    ("Grapes", 69, 0.7, 18.0, 0.2, 0.9, 15.0, 2),
    ("Pear", 57, 0.4, 15.0, 0.1, 3.1, 9.8, 1),
    ("Kiwi", 61, 1.1, 15.0, 0.5, 3.0, 9.0, 3),
    ("Avocado", 160, 2.0, 9.0, 15.0, 6.7, 0.7, 7),
    # CARBS - Vegetables (starchy)
    ("Sweet Potato (baked)", 103, 2.3, 24.0, 0.1, 3.8, 7.4, 41),
    ("White Potato (baked)", 93, 2.5, 21.0, 0.1, 2.1, 1.1, 6),
    ("Corn (cooked)", 96, 3.4, 21.0, 1.5, 2.4, 4.5, 15),
    ("Peas (frozen, cooked)", 84, 5.4, 14.0, 0.4, 4.5, 5.5, 108),
    # VEGETABLES (non-starchy)
    ("Broccoli (cooked)", 55, 3.7, 11.0, 0.6, 5.1, 2.2, 41),
    ("Spinach (raw)", 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79),
    ("Kale (raw)", 49, 4.3, 9.0, 0.9, 3.6, 2.3, 38),
    ("Lettuce (romaine)", 17, 1.2, 3.3, 0.3, 2.1, 1.2, 8),
    ("Carrot", 41, 0.9, 10.0, 0.2, 2.8, 4.7, 69),
    ("Cucumber", 15, 0.7, 3.6, 0.1, 0.5, 1.7, 2),
    ("Tomato", 18, 0.9, 3.9, 0.2, 1.2, 2.6, 5),
    ("Bell Pepper (red)", 31, 1.0, 6.0, 0.3, 2.1, 4.2, 4),
    ("Onion", 40, 1.1, 9.3, 0.1, 1.7, 4.2, 4),
    ("Mushrooms (white, cooked)", 28, 2.2, 5.3, 0.5, 1.4, 2.0, 9),
    ("Zucchini (cooked)", 17, 1.2, 3.5, 0.3, 1.0, 2.5, 3),
    ("Asparagus (cooked)", 22, 2.4, 4.1, 0.2, 2.1, 1.3, 14),
    ("Green Beans (cooked)", 35, 1.8, 7.1, 0.3, 3.4, 1.4, 1),
    ("Cauliflower (cooked)", 23, 1.8, 4.1, 0.3, 2.3, 1.5, 10),
    ("Celery (raw)", 16, 0.7, 3.0, 0.2, 1.6, 1.3, 80),
    # FATS
    ("Olive Oil", 884, 0.0, 0.0, 100.0, 0.0, 0.0, 2),
    ("Coconut Oil", 862, 0.0, 0.0, 100.0, 0.0, 0.0, 0),
    ("Butter", 717, 0.9, 0.1, 81.0, 0.0, 0.1, 643),
    ("Almonds", 579, 21.0, 22.0, 50.0, 12.5, 4.4, 1),
    ("Walnuts", 654, 15.0, 14.0, 65.0, 6.7, 2.6, 2),
    ("Cashews", 553, 18.0, 30.0, 44.0, 3.3, 5.9, 12),
    ("Peanuts", 567, 26.0, 16.0, 49.0, 8.5, 4.7, 18),
    ("Peanut Butter", 598, 25.0, 20.0, 51.0, 6.0, 9.0, 459),
    ("Almond Butter", 614, 21.0, 19.0, 56.0, 10.0, 4.4, 3),
    ("Chia Seeds", 486, 17.0, 42.0, 31.0, 34.0, 0.0, 16),
    ("Flaxseeds", 534, 18.0, 29.0, 42.0, 27.0, 1.5, 30),
    ("Sunflower Seeds", 584, 21.0, 20.0, 51.0, 8.6, 2.6, 9),
    # LEGUMES
    ("Lentils (cooked)", 116, 9.0, 20.0, 0.4, 7.9, 1.8, 2),
    ("Black Beans (cooked)", 132, 8.9, 24.0, 0.5, 8.7, 0.3, 1),
    ("Chickpeas (cooked)", 164, 8.9, 27.0, 2.6, 7.6, 4.8, 7),
    ("Kidney Beans (cooked)", 127, 8.7, 22.0, 0.5, 6.4, 0.3, 2),
    ("Edamame (cooked)", 121, 11.0, 9.9, 5.2, 5.2, 2.2, 63),
    ("Tofu (firm)", 144, 17.0, 3.0, 9.0, 0.3, 0.6, 15),
    ("Tempeh", 193, 20.0, 8.0, 11.0, 0.0, 0.0, 9),
    # DAIRY EXTRAS
    ("Cream Cheese", 342, 6.0, 4.1, 34.0, 0.0, 3.2, 321),
    ("Sour Cream", 198, 2.4, 4.6, 19.0, 0.0, 3.8, 53),
    ("Heavy Cream", 340, 2.8, 2.8, 36.0, 0.0, 2.8, 27),
    ("Parmesan Cheese", 431, 38.0, 3.2, 29.0, 0.0, 0.9, 1602),
    ("Feta Cheese", 264, 14.0, 4.1, 21.0, 0.0, 4.1, 1116),
    # SNACKS & CONDIMENTS
    ("Rice Cakes (plain)", 387, 8.2, 82.0, 2.5, 2.6, 0.7, 7),
    ("Dark Chocolate (70%)", 598, 7.8, 46.0, 43.0, 10.9, 24.0, 20),
    ("Protein Bar (avg)", 377, 24.0, 42.0, 11.0, 5.0, 14.0, 250),
    ("Granola (plain)", 471, 10.0, 64.0, 20.0, 6.0, 22.0, 33),
    ("Crackers (whole wheat)", 431, 10.0, 67.0, 15.0, 9.0, 3.0, 500),
    ("Popcorn (air-popped)", 387, 13.0, 78.0, 5.0, 15.0, 0.9, 8),
    ("Hummus", 166, 7.9, 14.0, 10.0, 6.0, 0.7, 379),
    ("Ketchup", 101, 1.1, 25.0, 0.1, 0.3, 22.0, 907),
    ("Mayonnaise", 680, 0.9, 0.6, 75.0, 0.0, 0.6, 635),
    ("Hot Sauce", 11, 0.5, 1.0, 0.5, 0.5, 0.6, 920),
    # BEVERAGES (per 100ml)
    ("Whole Milk (liquid)", 61, 3.2, 4.8, 3.3, 0.0, 5.0, 44),
    ("Orange Juice", 45, 0.7, 10.0, 0.2, 0.2, 8.4, 1),
    ("Coffee (black)", 2, 0.3, 0.0, 0.0, 0.0, 0.0, 2),
    ("Sports Drink (Gatorade)", 26, 0.0, 6.5, 0.0, 0.0, 6.5, 52),
    ("Protein Shake (whey+milk)", 65, 8.0, 5.0, 1.5, 0.0, 4.0, 50),
    # BREAKFAST FOODS
    ("Pancakes (plain)", 227, 6.4, 28.0, 10.0, 0.9, 4.5, 475),
    ("Waffles (plain)", 291, 7.9, 33.0, 14.0, 1.1, 3.8, 565),
    ("Scrambled Eggs", 149, 10.0, 1.2, 11.0, 0.0, 1.2, 146),
    ("French Toast", 229, 8.3, 26.0, 10.0, 1.0, 7.2, 230),
    ("Granola Bar", 471, 9.0, 61.0, 21.0, 3.7, 27.0, 135),
    # FAST FOOD / COMMON MEALS
    ("Burger Bun", 277, 9.4, 51.0, 3.8, 2.0, 6.0, 418),
    ("French Fries (fast food)", 312, 3.4, 41.0, 15.0, 3.8, 0.3, 210),
    ("Pizza (cheese, thin crust)", 266, 11.0, 33.0, 10.0, 2.3, 3.6, 600),
    ("Mac and Cheese (boxed)", 349, 11.0, 49.0, 12.0, 1.5, 6.5, 549),
    ("Burrito Bowl (rice+chicken)", 170, 12.0, 20.0, 4.0, 2.0, 1.0, 350),
    # SOUPS
    ("Chicken Noodle Soup (canned)", 62, 3.8, 7.8, 1.5, 0.8, 1.0, 780),
    ("Tomato Soup (canned)", 73, 1.6, 14.0, 1.8, 1.0, 9.0, 456),
    ("Lentil Soup", 99, 6.3, 15.0, 1.5, 4.0, 2.5, 386),
    # SAUCES / DRESSINGS
    ("Marinara Sauce", 65, 1.9, 11.0, 1.8, 2.4, 7.0, 438),
    ("Alfredo Sauce", 135, 3.3, 7.5, 11.0, 0.2, 2.0, 420),
    ("Soy Sauce", 53, 8.1, 4.9, 0.6, 0.8, 1.9, 5720),
    ("BBQ Sauce", 172, 1.5, 40.0, 0.5, 0.9, 33.0, 843),
    ("Ranch Dressing", 449, 1.5, 5.0, 47.0, 0.0, 4.0, 820),
    ("Balsamic Vinegar", 88, 0.5, 17.0, 0.1, 0.0, 15.0, 23),
    # FROZEN / CONVENIENCE
    ("Frozen Peas (cooked)", 80, 5.4, 14.0, 0.4, 4.5, 5.5, 108),
    ("Frozen Broccoli (cooked)", 35, 2.8, 6.6, 0.4, 3.3, 1.7, 41),
    ("Frozen Mixed Vegetables", 65, 3.1, 13.0, 0.4, 3.6, 3.8, 32),
    # MISC HIGH PROTEIN
    ("Jerky (beef)", 410, 33.0, 11.0, 26.0, 0.5, 9.0, 1760),
    ("String Cheese", 283, 20.0, 2.4, 22.0, 0.0, 1.5, 600),
    ("Hard Boiled Egg", 155, 13.0, 1.1, 11.0, 0.0, 1.1, 124),
    ("Canned Chicken", 120, 22.0, 0.0, 3.0, 0.0, 0.0, 340),
    ("Deli Turkey", 107, 18.0, 2.5, 3.0, 0.0, 1.5, 1050),
    # GRAINS EXTRA
    ("Barley (cooked)", 123, 2.3, 28.0, 0.4, 3.8, 0.3, 3),
    ("Bulgur (cooked)", 83, 3.1, 19.0, 0.2, 4.5, 0.1, 5),
    ("Buckwheat (cooked)", 92, 3.4, 20.0, 0.6, 2.7, 0.9, 4),
    ("Millet (cooked)", 119, 3.5, 23.0, 1.0, 1.3, 0.0, 2),
    ("Amaranth (cooked)", 102, 3.8, 19.0, 1.6, 2.1, 0.0, 6),
    # PROTEIN EXTRAS
    ("Seitan", 370, 75.0, 14.0, 1.9, 0.6, 0.0, 640),
    ("Lentil Dahl", 90, 5.5, 13.0, 1.5, 4.0, 2.0, 280),
    ("Black Bean Burger", 190, 12.0, 20.0, 7.0, 6.0, 2.0, 400),
    ("Protein Oatmeal", 140, 12.0, 20.0, 3.0, 3.0, 3.0, 150),
    # NUTS EXTRA
    ("Pistachios", 562, 20.0, 28.0, 45.0, 10.0, 7.7, 1),
    ("Macadamia Nuts", 718, 8.0, 14.0, 76.0, 8.6, 4.6, 5),
    ("Pecans", 691, 9.2, 14.0, 72.0, 9.6, 4.0, 0),
    ("Brazil Nuts", 656, 14.0, 12.0, 66.0, 7.5, 2.3, 3),
    # SWEETS / TREATS
    ("Ice Cream (vanilla)", 207, 3.5, 24.0, 11.0, 0.0, 21.0, 80),
    ("Honey", 304, 0.3, 82.0, 0.0, 0.2, 82.0, 4),
    ("Maple Syrup", 260, 0.0, 67.0, 0.1, 0.0, 60.0, 12),
    ("Jam (strawberry)", 278, 0.4, 69.0, 0.1, 1.0, 52.0, 32),
    ("Chocolate Chip Cookies", 488, 5.4, 63.0, 25.0, 1.6, 38.0, 252),
    ("Brownie", 466, 5.0, 57.0, 24.0, 2.0, 40.0, 170),
    # PLANT-BASED
    ("Soy Milk", 54, 3.3, 6.3, 1.8, 0.5, 4.5, 51),
    ("Almond Milk (unsweetened)", 15, 0.6, 0.6, 1.2, 0.4, 0.0, 150),
    ("Oat Milk", 47, 1.0, 8.0, 1.5, 0.3, 5.0, 100),
    ("Coconut Milk (canned)", 197, 2.3, 6.0, 21.0, 0.0, 3.3, 13),
    ("Nutritional Yeast", 325, 40.0, 42.0, 4.4, 14.0, 0.5, 50),
    ("Miso Paste", 199, 12.0, 26.0, 6.0, 5.4, 6.0, 3728),
    # SUSHI / ASIAN
    ("White Rice (sushi)", 150, 2.7, 33.0, 0.3, 0.4, 0.0, 1),
    ("Edamame (shelled)", 121, 11.0, 9.9, 5.2, 5.2, 2.2, 63),
    ("Miso Soup", 40, 2.7, 4.5, 1.7, 0.6, 1.8, 900),
    ("Sashimi Salmon", 208, 20.0, 0.0, 13.0, 0.0, 0.0, 59),
    # ADDITIONAL COMMON
    ("Cream of Wheat (cooked)", 71, 2.3, 15.0, 0.3, 0.6, 0.3, 106),
    ("Grits (cooked)", 71, 1.7, 15.0, 0.4, 0.4, 0.1, 270),
    ("Bisquick (pancake mix, dry)", 383, 8.3, 63.0, 11.0, 2.7, 8.0, 1067),
    ("Naan Bread", 265, 9.0, 50.0, 5.0, 2.0, 3.0, 460),
    ("Pita Bread", 275, 9.1, 56.0, 1.2, 2.2, 0.8, 536),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM foods"))
        count = result.scalar()
        if count and count > 0:
            print(f"Already seeded ({count} foods). Skipping.")
            return

        for name, cal, prot, carbs, fat, fiber, sugar, sodium in FOODS:
            await db.execute(
                text("""
                    INSERT INTO foods
                        (name, calories_per_100g, protein_g, carbs_g, fat_g,
                         fiber_g, sugar_g, sodium_mg)
                    VALUES
                        (:name, :cal, :prot, :carbs, :fat,
                         :fiber, :sugar, :sodium)
                """),
                dict(name=name, cal=cal, prot=prot, carbs=carbs, fat=fat,
                     fiber=fiber, sugar=sugar, sodium=sodium),
            )
        await db.commit()
        print(f"Seeded {len(FOODS)} foods.")


if __name__ == "__main__":
    asyncio.run(seed())
