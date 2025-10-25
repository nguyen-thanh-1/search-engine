import requests
import json
import time


class TheMealDBCrawler:
    """
    A crawler for TheMealDB public API
    - Thu thập dữ liệu món ăn theo từ khóa hoặc thể loại
    - Lưu dữ liệu ra file JSON
    """

    def __init__(self, delay=1):
        self.base_url = "https://www.themealdb.com/api/json/v1/1/"
        self.delay = delay
        self.recipes = []

    # ==============================
    # Tìm món ăn theo từ khóa
    # ==============================
    def search_by_keyword(self, keyword: str):
        """Tìm món ăn theo tên hoặc nguyên liệu"""
        url = f"{self.base_url}search.php?s={keyword}"
        res = requests.get(url)
        data = res.json()

        if data["meals"]:
            for meal in data["meals"]:
                self.recipes.append(self._extract_meal(meal))
        time.sleep(self.delay)

    # ==============================
    # Tìm món theo thể loại (category)
    # ==============================
    def get_by_category(self, category: str):
        """Lấy danh sách món theo thể loại"""
        url = f"{self.base_url}filter.php?c={category}"
        res = requests.get(url)
        data = res.json()

        if data["meals"]:
            for meal in data["meals"]:
                meal_id = meal["idMeal"]
                # Lấy chi tiết từng món
                detail = self._get_detail(meal_id)
                if detail:
                    self.recipes.append(detail)
        time.sleep(self.delay)

    # ==============================
    # Hàm phụ: Lấy chi tiết món ăn theo ID
    # ==============================
    def _get_detail(self, meal_id: str):
        url = f"{self.base_url}lookup.php?i={meal_id}"
        res = requests.get(url)
        data = res.json()

        if data["meals"]:
            meal = data["meals"][0]
            return self._extract_meal(meal)
        return None

    # ==============================
    # Chuẩn hóa dữ liệu món ăn
    # ==============================
    def _extract_meal(self, meal):
        """Trích thông tin quan trọng từ JSON"""
        ingredients = [
            meal.get(f"strIngredient{i}")
            for i in range(1, 21)
            if meal.get(f"strIngredient{i}")
        ]

        return {
            "id": meal["idMeal"],
            "title": meal["strMeal"],
            "category": meal["strCategory"],
            "area": meal["strArea"],
            "instructions": meal["strInstructions"],
            "image": meal["strMealThumb"],
            "ingredients": ingredients,
        }

    # ==============================
    # Lưu dữ liệu ra file
    # ==============================
    def save_to_json(self, filename="recipes.json"):
        """Lưu dữ liệu món ăn ra file JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.recipes, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu {len(self.recipes)} món ăn vào {filename}")

    # ==============================
    # Chạy nhiều từ khóa
    # ==============================
    def run_by_keywords(self, keywords):
        """Thu thập món ăn dựa theo danh sách từ khóa"""
        for key in keywords:
            print(f"🔍 Đang thu thập món: {key} ...")
            self.search_by_keyword(key)
        self.save_to_json("recipes_by_keywords.json")

    # ==============================
    # Chạy nhiều thể loại
    # ==============================
    def run_by_categories(self, categories):
        """Thu thập món ăn dựa theo danh sách thể loại"""
        for cat in categories:
            print(f"🍽️ Đang thu thập thể loại: {cat} ...")
            self.get_by_category(cat)
        self.save_to_json("recipes_by_categories.json")


# ==============================
# Demo chạy thử
# ==============================
if __name__ == "__main__":
    crawler = TheMealDBCrawler(delay=1)

    # Cách 1: Crawl theo từ khóa
    keywords = ["chicken", "beef", "rice", "salad"]
    crawler.run_by_keywords(keywords)

    # Cách 2: Crawl theo thể loại (có thể mở rộng)
    categories = ["Seafood", "Dessert", "Vegetarian"]
    crawler.run_by_categories(categories)
