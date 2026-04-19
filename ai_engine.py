import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the AI model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_food_profile(user_input):
    """Sends food data to AI and returns structured profile."""
    system_prompt = f"""
    You are a clinical nutritionist. Analyze the following food: {user_input}.
    Return the response in this exact format:
    
    ##  Food Profile: [Food Name]
    **Estimated Calories:** [Calorie count for the quantity]
    **Macronutrients:** (Protein, Carbs, Fats)
    
    ### ✅ Advantages
    * [Benefit 1]
    * [Benefit 2]
    
    ### ⚠️ Disadvantages
    * [Risk/Allergen 1]
    * [Risk/Allergen 2]
    
    ### 👨‍⚕️ Recommendations
    * **Who should consume:** [Groups like athletes, etc.]
    * **Who should avoid:** [Groups like diabetics, etc.]
    """
    
    try:
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"