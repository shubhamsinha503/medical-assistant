import google.generativeai as genai
import PIL.Image
import streamlit as st
import requests

# Function to get the Gemini AI response
def get_gemini_response(api_key, prompt, image):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([prompt, image])
    return response.text

# Fetch nearby doctors using Google Maps API
def get_nearby_doctors(location, specialty):
    try:
        api_key = "google maps"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=doctors+{specialty}+near+{location}&key={api_key}"

        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            doctors = []
            for result in results:
                doctor_info = {
                    "name": result.get("name"),
                    "address": result.get("formatted_address"),
                    "rating": result.get("rating", "N/A"),
                    "user_ratings_total": result.get("user_ratings_total", 0),
                }
                doctors.append(doctor_info)
            return doctors
        else:
            st.error(f"Error fetching doctors: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching doctors: {e}")
        return []

# Streamlit app customization
st.set_page_config(
    page_title="Gemini Vision Bot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 8px 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stHeader {
        text-align: center;
        font-size: 32px;
        color: #2c3e50;
    }
    .stSubheader {
        color: #16a085;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header with an image
#st.image("12.png", use_column_width=False, caption="Welcome to Gemini Vision Bot",width=600)
left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image("12.png")
# Replace with your image path
st.markdown("<div class='stHeader'>GenAI Medical Application</div>", unsafe_allow_html=True)

# Sidebar for input fields
st.sidebar.title("Input Details")
st.sidebar.image("122.jpg", use_column_width=True, caption="Input Patient Data")  # Replace with your image path
api_key = "gemini api key"
location = st.sidebar.text_input("Enter your location (e.g., Delhi): ")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Load image without displaying it
if uploaded_file is not None:
    image = PIL.Image.open(uploaded_file)
else:
    image = None

# Button to submit the request
if st.sidebar.button("Generate AI Report"):
    if api_key and image is not None and location:
        try:
            # Generate AI response
            prompt = "generate an AI report of the detected disease in image like finding, precautions, recommendations, and suggest the kind of doctor to be consulted and also give some risk graph and give no disclaimer"
            ai_response = get_gemini_response(api_key, prompt, image)
            st.title("AI Report:")
            st.markdown(f"<div class='stSubheader'>{ai_response}</div>", unsafe_allow_html=True)

            # Extract doctor type from the response
            doctor_type = "dermatologist"  # Replace with logic to parse `ai_response`

            # Find nearby doctors based on the detected doctor type
            st.subheader(f"Nearby {doctor_type.capitalize()}s:")
            doctors = get_nearby_doctors(location, doctor_type)
            if doctors:
                for doctor in doctors:
                    st.markdown(
                        f"""
                        - **Name**: {doctor['name']}
                        - **Address**: {doctor['address']}
                        - **Rating**: {doctor['rating']} ({doctor['user_ratings_total']} reviews)
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write(f"No {doctor_type}s found nearby.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please provide all required inputs.")

# Add a footer image
#st.image("footer_image.jpg", use_column_width=True, caption="Empowering Medical Decisions with AI")  # Replace with your image path

# Footer text
st.markdown(
    """
    <hr>
    <div style="text-align: center; font-size: 14px;">
        Powered by <b>Gemini AI</b> | Developed with ❤️ 
    </div>
    """,
    unsafe_allow_html=True
)
