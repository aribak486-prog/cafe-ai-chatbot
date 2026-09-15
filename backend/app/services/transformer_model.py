import json
import re
from app.config import get_settings
from app.core.cafe_data import CAFE_DATA
from app.core.prompts import SYSTEM_PROMPT
from app.models.schemas import Message


class CafeAdvisorModel:
    """Cafe-grounded responder with an optional Hugging Face Transformer fallback."""
    def __init__(self) -> None:
        self.settings = get_settings()
        self.tokenizer = None
        self.model = None
        self.load_error: str | None = None

    def _load(self) -> None:
        if self.tokenizer is not None or self.load_error is not None:
            return
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.settings.model_name)
        except Exception as error:  # App remains useful offline via data-grounded answers.
            self.load_error = str(error)

    def _matching_items(self, question: str) -> list[dict]:
        q = question.lower()
        return [item for item in CAFE_DATA["menu"] if item["name"].lower() in q or any(word in q for word in item["name"].lower().split() if len(word) > 3)]

    def _grounded_response(self, question: str) -> str | None:
        q = question.lower()
        matches = self._matching_items(q)
        if any(x in q for x in ["price", "cost", "how much"]):
            if matches:
                return "\n".join(f"{item['name']} costs ${item['price']:.2f}." for item in matches)
            return "I don't currently have that item in the cafe menu data, so I can't confirm its price."
        if "ingredient" in q or "contain" in q or "made of" in q:
            if matches:
                return "\n".join(f"{item['name']} contains: {', '.join(item['ingredients'])}." for item in matches)
            return "I don't currently have ingredient information for that item."
        if any(x in q for x in ["open", "hour", "closing", "close"]):
            day = next((d for d in CAFE_DATA['opening_hours'] if d in q), None)
            if day:
                return f"On {day.title()}, we are open {CAFE_DATA['opening_hours'][day]}."
            return "Our hours are: " + "; ".join(f"{d.title()}: {h}" for d, h in CAFE_DATA['opening_hours'].items()) + "."
        if any(x in q for x in ["where", "location", "address"]):
            return f"{CAFE_DATA['name']} is at {CAFE_DATA['location']}."
        if "popular" in q or "recommend" in q or "suggest" in q:
            items = [x['name'] for x in CAFE_DATA['menu'] if x['popular']]
            return "Our popular picks are " + ", ".join(items[:-1]) + f", and {items[-1]}."
        if "vegan" in q or "vegetarian" in q or "diet" in q:
            label = "Vegan" if "vegan" in q else "Vegetarian"
            items = [x['name'] for x in CAFE_DATA['menu'] if x['dietary'] == label]
            return f"{label} options: " + ", ".join(items) + "."
        if any(x in q for x in ["menu", "drink", "food", "coffee", "tea", "dessert", "available", "have"]):
            category = next((c for c in ["coffee", "tea", "food", "dessert"] if c in q), None)
            items = [x for x in CAFE_DATA['menu'] if not category or x['category'].lower() == category]
            return "\n".join(f"• {x['name']} — ${x['price']:.2f}: {x['description']}" for x in items)
        if matches:
            x = matches[0]
            return f"{x['name']} is a {x['description'].lower()} and costs ${x['price']:.2f}."
        return None

    def generate_response(self, messages: list[Message]) -> str:
        question = messages[-1].content
        grounded = self._grounded_response(question)
        if grounded:
            return grounded
        cafe_terms = ["cafe", "menu", "price", "coffee", "food", "drink", "ingredient", "hours", "location", "recommend"]
        if not any(term in question.lower() for term in cafe_terms):
            return "I specialize in CafeAI Coffee House's menu and cafe information. What would you like to know about our food, drinks, prices, or hours?"
        self._load()
        if self.model is None or self.tokenizer is None:
            return "I don't currently have that information in the cafe data. I can help with our menu, prices, ingredients, popular items, hours, and location."
        prompt = f"{SYSTEM_PROMPT}\nCafe data: {json.dumps(CAFE_DATA)}\nQuestion: {question}\nAnswer:"
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            output = self.model.generate(**inputs, max_new_tokens=self.settings.max_new_tokens, do_sample=self.settings.temperature > 0, temperature=self.settings.temperature, top_p=self.settings.top_p)
            response = self.tokenizer.decode(output[0], skip_special_tokens=True).strip()
            return response or "I don't currently have that information in the cafe data."
        except Exception:
            return "I’m sorry, I couldn’t generate a response right now. Please try again."
