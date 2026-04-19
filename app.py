import streamlit as st
import google.generativeai as genai
import os
import json # New library to parse AI data
from dotenv import load_dotenv

# --- CONFIGURATION & SECURITY ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API Key exists
if not API_KEY:
    st.error("❌ Gemini API Key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)
# We use Gemini 1.5 Flash for speed and excellent structured output
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PAGE CONFIG (The Theme) ---
st.set_page_config(
    page_title="AI Food Profiler Pro",
    page_icon="🥗",
    layout="wide", # Use full width for a dashboard look
    initial_sidebar_state="collapsed"
)

# Custom CSS to inject modern styling (Rounded corners, Card styling)
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Style for Containers (Cards) */
    div[data-testid="stVerticalBlock"] > div:has(div.card) {
        border-radius: 15px;
        background-color: white;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    /* Headers inside cards */
    .card-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #000000;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --- AI LOGIC (Engineering JSON Output) ---
def get_structured_food_profile(user_input):
    """Requests data in strict JSON format for reliable parsing."""
    
    # We provide a blueprint of exactly how we want the data
    json_structure = """
    {
      "food_name": "String",
      "serving_size_info": "String",
      "calories": 123,
      "protein_g": 12.3,
      "carbs_g": 12.3,
      "fats_g": 12.3,
      "macro_summary": "Short text summary of macros",
      "micronutrients_high": ["vitamin 1", "mineral 1"],
      "advantages": ["Point 1", "Point 2"],
      "disadvantages": ["Risk 1", "Risk 2"],
      "consume_rec": ["Groups who benefit"],
      "avoid_rec": ["Groups with risks"]
    }
    """
    
    prompt = f"""
    You are a professional clinical nutritionist. 
    Analyze the food item: '{user_input}'.
    Based on standard dietary data, provide the nutritional profile.
    
    Return the response as a valid JSON object ONLY, strictly following this structure:
    {json_structure}
    
    Do not add extra explanations or Markdown code blocks. If data is unknown, use null.
    """
    
    try:
        # Generate the response
        response = model.generate_content(prompt)
        text_response = response.text
        
        # Clean up the response (Gemini sometimes adds ```json ... ``` tags)
        cleaned_text = text_response.strip().replace("```json", "").replace("```", "")
        
        # Convert text into a usable Python Dictionary
        return json.loads(cleaned_text)
    
    except json.JSONDecodeError:
        st.error("AI returned invalid data structure. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error connecting to AI: {str(e)}")
        return None


# --- USER INTERFACE DESIGN ---

# Header Section
st.markdown("<h1 style='text-align: center; color: #000000;'>🥗 AI Food Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280; font-size: 1.1rem;'>Professional nutritional analysis of any food or meal.</p>", unsafe_allow_html=True)
st.write("---")

# Input Section (Using a narrower column layout)
_, in_col, _ = st.columns([1, 2, 1])
with in_col:
    user_input = st.text_input("Enter Food (e.g., 300g Salmon, 1 slice Pizza)", placeholder="Describe what you ate...")
    analyze_btn = st.button("Generate Detailed Profile", use_container_width=True)

st.write("---")

# Output Section
if analyze_btn:
    if user_input:
        with st.spinner(f"Analyzing {user_input}..."):
            
            # Fetch the structured data
            food_data = get_structured_food_profile(user_input)
            
            # If the AI request failed, stop here
            if not food_data:
                st.stop()

            # The Dashboard Layout
            
            # Row 1: The Overview Card
            st.markdown(f"### 📋 Analysis: {food_data['food_name']} ({food_data['serving_size_info']})")
            
            # Row 2: Macros and Overview side-by-side
            col1, col2 = st.columns([1, 1.5])
            
            # Macros Card (Visual Metrics)
            with col1:
                st.markdown("<div class='card'><div class='card-header'>Macronutrient Breakdown</div>", unsafe_allow_html=True)
                
                # Show Calories large
                st.metric("Estimated Calories", f"{food_data['calories']} kcal")
                
                # Show P/C/F in columns
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Protein", f"{food_data['protein_g']}g", help="Crucial for muscle repair")
                m_col2.metric("Carbs", f"{food_data['carbs_g']}g", help="Main energy source")
                m_col3.metric("Fats", f"{food_data['fats_g']}g", help="Energy and cell health")
                
                st.info(food_data['macro_summary'])
                st.markdown("</div>", unsafe_allow_html=True)
                
            # Micronutrients Card
            with col2:
                st.markdown("<div class='card'><div class='card-header'>Key Micronutrients (Vitamins/Minerals)</div>", unsafe_allow_html=True)
                if food_data['micronutrients_high']:
                    cols = st.columns(3)
                    # Loop through nutrients and spread across columns
                    for i, nutrient in enumerate(food_data['micronutrients_high']):
                        cols[i % 3].success(f"✨ {nutrient}")
                else:
                    st.write("Standard micronutrient levels.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.write("") # Spacer

            # Row 3: Pros/Cons side-by-side
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("<div class='card'><div class='card-header' style='color: #166534;'>✅ Key Advantages</div>", unsafe_allow_html=True)
                for pt in food_data['advantages']:
                    st.markdown(f"**+** {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col4:
                st.markdown("<div class='card'><div class='card-header' style='color: #991b1b;'>⚠️ Potential Disadvantages</div>", unsafe_allow_html=True)
                if food_data['disadvantages']:
                    for pt in food_data['disadvantages']:
                        st.markdown(f"**-** {pt}")
                else:
                    st.write("No major negative aspects.")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("") # Spacer

            # Row 4: Recommendations Card (Full width)
            st.markdown("<div class='card'><div class='card-header'>👨‍⚕️ Professional Recommendations</div>", unsafe_allow_html=True)
            rec_col1, rec_col2 = st.columns(2)
            with rec_col1:
                st.subheader("Ideal for:")
                for pt in food_data['consume_rec']:
                    st.markdown(f"👍 {pt}")
            with rec_col2:
                st.subheader("Caution for:")
                for pt in food_data['avoid_rec']:
                    st.markdown(f"🛑 {pt}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Mandatory Disclaimer
            st.write("---")
            st.caption("🚨 IMPORTANT: This information is AI-generated based on statistical dietary data. It does not replace advice from a qualified medical professional or registered dietitian.")

    else:
        st.warning("Please enter a food item.")