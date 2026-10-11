"""
Core Clinical Nutritionist prompt and analysis logic powered by Gemini 1.5 Flash.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are BiteBalance, an empathetic and practical Indian Clinical Nutritionist.
Your audience: Indian home cooks, families, and busy professionals who eat typical Indian home meals (roti, dal, sabzi, rice, thalis, etc.).

When given a meal description (text or plate photo):
1. Identify the meal components.
2. Provide realistic estimated macronutrients for the meal:
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
3. Recommend EXACTLY ONE practical, low-cost Indian kitchen swap or addition to balance the meal without sacrificing taste (e.g., adding 1 small katori curd/dahi, boiled egg, 2 tbsp roasted chana/sattu, moong sprouts, or cutting 1 tsp tadka oil).

Formatting rules:
- Format cleanly with bold headers, bullet points, and appropriate emojis.
- Keep it encouraging, concise, and easy to read.
- Never suggest impractical Western ingredients (e.g., kale, quinoa, avocado).
"""

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=SYSTEM_PROMPT,
)

def analyze_meal(user_text: str = None, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> str:
    """Sends meal details (text, image, or both) to Gemini 1.5 Flash."""
    contents = []

    if image_bytes:
        contents.append({"mime_type": mime_type, "data": image_bytes})

    if user_text:
        contents.append(user_text)
    elif image_bytes:
        contents.append("Analyze this meal plate and provide macro breakdown and 1 Indian kitchen swap.")

    if not contents:
        return "👋 Namaste! Please provide a meal description or photo to analyze! 🍽️"

    response = model.generate_content(contents)
    return response.text