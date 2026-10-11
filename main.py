import streamlit as st
from PIL import Image
from nutrition_core import analyze_meal

st.set_page_config(
    page_title="BiteBalance | Indian Meal Coach",
    page_icon="🥗",
    layout="centered"
)

st.title("🥗 BiteBalance")
st.caption("Balanced Indian Nutrition from Your Existing Kitchen")

tab1, tab2 = st.tabs(["📸 Upload Photo", "✍️ Describe Meal"])

# Tab 1: Image Analysis
with tab1:
    uploaded_file = st.file_uploader(
        "Upload a photo of your plate or thali:", 
        type=["jpg", "jpeg", "png", "webp"]
    )
    photo_notes = st.text_input(
        "Optional notes (e.g., '2 rotis made with ghee'):", 
        key="photo_notes"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Meal", use_column_width=True)
        
    if st.button("Analyze Plate Photo", type="primary", disabled=uploaded_file is None):
        with st.spinner("Analyzing your plate and calculating macros..."):
            img_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type or "image/jpeg"
            result = analyze_meal(
                user_text=photo_notes if photo_notes else None,
                image_bytes=img_bytes,
                mime_type=mime_type
            )
            st.divider()
            st.markdown(result)

# Tab 2: Text Analysis
with tab2:
    meal_text = st.text_area(
        "What did you eat?",
        placeholder="e.g., 2 parathas with aloo filling, 1 cup curd, and mango pickle",
        height=100
    )
    
    if st.button("Analyze Meal Text", type="primary"):
        if not meal_text.strip():
            st.warning("Please enter your meal details first.")
        else:
            with st.spinner("Analyzing macros and finding kitchen tweaks..."):
                result = analyze_meal(user_text=meal_text.strip())
                st.divider()
                st.markdown(result)