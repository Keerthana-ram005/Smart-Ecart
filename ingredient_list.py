RAW_INGREDIENTS = [
    "egg", "bread", "milk", "butter", "oil", "salt", "sugar", "flour",
    "rice", "onion", "tomato", "potato", "garlic", "ginger", "chili",
    "pepper", "turmeric", "cumin", "cheese", "chicken", "fish", "beef",
    "pork", "lamb", "corn", "bean", "lentil", "pasta", "noodle", "soy sauce",
    "vinegar", "lemon", "lime", "orange", "apple", "banana", "strawberry",
    "blueberry", "carrot", "broccoli", "spinach", "cabbage", "lettuce",
    "mushroom", "basil", "oregano", "parsley", "cilantro", "thyme", "rosemary",
    "cinnamon", "nutmeg", "clove", "cardamom", "coriander", "mustard",
    "mayonnaise", "ketchup", "honey", "maple syrup", "chocolate", "cocoa",
    "vanilla", "baking powder", "baking soda", "yeast", "almond", "walnut",
    "peanut", "cashew", "pecan", "sesame", "water", "cream", "yogurt",
    "bacon", "sausage", "ham", "shrimp", "crab", "lobster", "salmon",
    "tuna", "cod", "oat", "quinoa", "barley", "wheat", "rye", "coconut",
    "pineapple", "mango", "peach", "pear", "plum", "cherry", "grape",
    "melon", "watermelon", "pumpkin", "squash", "zucchini", "eggplant",
    "bell pepper", "jalapeno", "habanero", "paprika", "chili powder",
    "cayenne", "beef broth", "chicken broth", "vegetable broth"
]

PLURAL_MAP = {
    "tomatoes": "tomato",
    "onions": "onion",
    "potatoes": "potato",
    "carrots": "carrot",
    "eggs": "egg",
    "apples": "apple",
    "strawberries": "strawberry",
    "blueberries": "blueberry",
    "mushrooms": "mushroom",
    "beans": "bean",
    "lentils": "lentil",
    "noodles": "noodle",
    "lemons": "lemon",
    "limes": "lime",
    "oranges": "orange",
    "bananas": "banana",
    "peaches": "peach",
    "pears": "pear",
    "plums": "plum",
    "cherries": "cherry",
    "grapes": "grape",
    "melons": "melon",
    "pumpkins": "pumpkin",
    "zucchinis": "zucchini",
    "eggplants": "eggplant",
    "peppers": "pepper",
    "jalapenos": "jalapeno",
    "habaneros": "habanero"
}

def normalize_ingredient_name(name: str) -> str:
    """Lowercase the name and apply plural mapping normalization."""
    name = name.strip().lower()
    return PLURAL_MAP.get(name, name)
