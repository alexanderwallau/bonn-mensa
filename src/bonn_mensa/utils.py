import datetime
import re
import unicodedata
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import Any, Optional

import holidays

content_strings = {
    "NEW_INFOS_ALLERGENS": {
        "de": "Allergene",
        "en": "Allergens",
    },
    "NEW_INFOS_ADDITIVES": {
        "de": "Zusatzstoffe",
        "en": "Additives",
    },
    "PRICE_CATEGORY_STUDENT": {
        "de": "Stud.",
        "en": "Student",
    },
    "PRICE_CATEGORY_STAFF": {
        "de": "Bed.",
        "en": "Staff",
    },
    "PRICE_CATEGORY_GUEST": {
        "de": "Gast",
        "en": "Guest",
    },
}


def slugify(value: Any, allow_unicode: bool = False) -> str:
    """Slugify a value.

    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def get_mensa_date() -> datetime.date:
    # Since the canteenes ar elocated in NRW get the public holidays for NRW
    nrw_holidays = holidays.country_holidays("DE", subdiv="NW")

    date = datetime.date.today()
    # Initialize the next working day as the day after today
    next_working_day = date + datetime.timedelta()

    # Loop until we find a day that is not a weekend or a public holiday
    while next_working_day.weekday() >= 5 or next_working_day in nrw_holidays:
        next_working_day += datetime.timedelta(days=1)

    return next_working_day


class Meal:
    def __init__(self, title: str) -> None:
        self.title = title
        self.allergens: list[str] = []
        self.additives: list[str] = []
        self.student_price: Optional[int] = None
        self.staff_price: Optional[int] = None
        self.guest_price: Optional[int] = None

    def add_allergen(self, allergen: str) -> None:
        self.allergens.append(allergen)

    def add_additive(self, additive: str) -> None:
        self.additives.append(additive)

    def __repr__(self) -> str:
        return f"Meal('{self.title}')"


class Category:
    def __init__(self, title: str) -> None:
        self.title = title
        self.meals: list[Meal] = []

    def add_meal(self, meal: Meal) -> None:
        self.meals.append(meal)

    def __repr__(self) -> str:
        return f"({self.title}: {self.meals})"


class SimpleMensaResponseParser(HTMLParser):
    def __init__(self, lang: str, verbose: bool = False) -> None:
        super().__init__()
        self.curr_category: Optional[Category] = None
        self.curr_meal: Optional[Meal] = None

        self.last_tag: Optional[str] = None
        self.last_nonignored_tag: Optional[str] = None
        self.categories: list[Category] = []
        self.mode = "INIT"

        self.lang = lang
        self.verbose = verbose

        self.meta_data: list[str] = []

    def start_new_category(self) -> None:
        if self.curr_category:
            if self.curr_meal:
                self.curr_category.add_meal(self.curr_meal)
                self.curr_meal = None
            self.categories.append(self.curr_category)
            self.curr_category = None

        self.mode = "NEW_CAT"

    def start_new_meal(self) -> None:
        if not self.curr_category:
            self.curr_category = Category("DUMMY-Name")

        if self.curr_meal:
            self.curr_category.add_meal(self.curr_meal)
            self.curr_meal = None

        self.mode = "NEW_MEAL"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # skip non-empty attributes
        if attrs or tag not in ["h2", "h5", "strong", "p", "th", "td", "br"]:
            self.mode = "IGNORE"
            return

        self.last_nonignored_tag = tag
        if tag == "h2":
            self.start_new_category()
        elif tag == "h5":
            self.start_new_meal()
        elif tag == "strong":
            self.mode = "NEW_INFOS"
        elif tag == "p":
            if not self.curr_meal and not self.curr_category:
                self.mode = "INFO"
        elif tag == "th":
            self.mode = "NEW_PRICE_CAT"
        elif tag == "td":
            pass

    def parse_price(self, price: str) -> int:
        return int("".join(digit for digit in price if digit.isdigit()))

    def handle_data(self, data: str) -> None:
        if self.mode == "IGNORE" or not data.strip():
            return
        if self.mode in ["INIT", "INFO"]:
            self.meta_data.append(data)
            return
        data = data.strip()
        if self.mode == "NEW_CAT":
            self.curr_category = Category(data)
            if self.verbose:
                print(f"Creating new category {data}")
        elif self.mode == "NEW_MEAL":
            self.curr_meal = Meal(data)
            if self.verbose:
                print(f"\tCreating new meal {data}")
        elif self.mode == "NEW_INFOS":
            if data == content_strings["NEW_INFOS_ALLERGENS"][self.lang]:
                self.mode = "NEW_ALLERGENS"
            elif data == content_strings["NEW_INFOS_ADDITIVES"][self.lang]:
                self.mode = "NEW_ADDITIVES"
            else:
                raise NotImplementedError(f"Mode NEW_INFOS with data {data}")
        elif self.mode == "NEW_ALLERGENS":
            if self.verbose:
                print(f"\t\tAdding new allergen: {data}")
            assert self.curr_meal is not None
            self.curr_meal.add_allergen(data)
        elif self.mode == "NEW_ADDITIVES":
            if self.verbose:
                print(f"\t\tAdding new additive: {data}")
            assert self.curr_meal is not None
            self.curr_meal.add_additive(data)
        elif self.mode == "NEW_PRICE_CAT":
            if data == content_strings["PRICE_CATEGORY_STUDENT"][self.lang]:
                self.mode = "NEW_PRICE_STUDENT"
            elif data == content_strings["PRICE_CATEGORY_STAFF"][self.lang]:
                self.mode = "NEW_PRICE_STAFF"
            elif data == content_strings["PRICE_CATEGORY_GUEST"][self.lang]:
                self.mode = "NEW_PRICE_GUEST"
            else:
                raise NotImplementedError(f"Mode NEW_PRICE_CAT with data {data}")
        elif self.mode == "NEW_PRICE_STUDENT":
            assert self.last_nonignored_tag == "td"
            assert self.curr_meal is not None
            self.curr_meal.student_price = self.parse_price(data)
        elif self.mode == "NEW_PRICE_STAFF":
            assert self.last_nonignored_tag == "td"
            assert self.curr_meal is not None
            self.curr_meal.staff_price = self.parse_price(data)
        elif self.mode == "NEW_PRICE_GUEST":
            assert self.last_nonignored_tag == "td"
            assert self.curr_meal is not None
            self.curr_meal.guest_price = self.parse_price(data)
        else:
            raise NotImplementedError(f"{self.last_nonignored_tag} with data {data}")

    def close(self) -> None:
        super().close()
        self.start_new_category()


def to_xml(categories: list[Category], meta_data: list[str], canteen_name: str) -> ET.Element:
    # Define namespaces
    ns = {
        "": "http://openmensa.org/open-mensa-v2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    # Register namespaces
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    # Create the root element with namespaces
    root = ET.Element(
        "openmensa",
        {
            "version": "2.1",
            "xmlns": ns[""],
            "xmlns:xsi": ns["xsi"],
            "xsi:schemaLocation": (
                "http://openmensa.org/open-mensa-v2 "
                "http://openmensa.org/open-mensa-v2.xsd"
            ),
        },
    )
    # Add version element
    version = ET.SubElement(root, "version")
    version.text = "5.04-4"

    # Create the canteen and Date element
    canteen = ET.SubElement(root, "canteen")
    day = ET.SubElement(canteen, "day")
    day.set("date", str(datetime.date.today()))

    if meta_data:
        meta_data = ET.SubElement(day, "meta_data")
        meta_data.text = ";".join(meta_data)

    # Create the meals element

    for cat in categories:
        categories = ET.SubElement(day, "category")
        categories.set("name", cat.title)
        for meal in cat.meals:
            meal_element = ET.SubElement(categories, "meal")
            name = ET.SubElement(meal_element, "name")
            name.text = meal.title
            # Add allergens and Additives
            allergens = ET.SubElement(meal_element, "note")
            combined_list = meal.allergens + meal.additives
            allergens.text = ", ".join(combined_list)
            # Add prices
            price = ET.SubElement(meal_element, "price")
            price.set("role", "student")
            if meal.student_price is not None:
                price.text = str(f"{meal.student_price / 100:.2f}")
            price = ET.SubElement(meal_element, "price")
            price.set("role", "employee")
            if meal.staff_price is not None:
                price.text = str(f"{meal.staff_price / 100:.2f}")
            price = ET.SubElement(meal_element, "price")
            price.set("role", "other")
            if meal.guest_price is not None:
                price.text = str(f"{meal.guest_price / 100:.2f}")

    return root