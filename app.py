import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# NVIDIA API endpoint
nvidia_api_url = "https://ai.api.nvidia.com/v1/vlm/nvidia/vila"

# Google Maps API key
google_maps_api_key = "google_api"


# Helper function to encode image
def encode_image_to_base64(upload_file):
    """Compress and encode image to base64 format."""
    try:
        image = Image.open(upload_file).convert("RGB")  # Ensure no alpha channel
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=70)  # Compress image
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Image encoding failed: {e}")
        return None


# Convert address to latitude and longitude
def geocode_address(address):
    """Geocode an address to latitude and longitude using Google Maps API."""
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": google_maps_api_key}
    response = requests.get(geocode_url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            location = results[0].get("geometry", {}).get("location", {})
            return location.get("lat"), location.get("lng")
        else:
            st.error("Could not find location. Please check the address.")
            return None, None
    else:
        st.error(f"Error geocoding address: {response.text}")
        return None, None


# Fetch nearby doctors based on disease type and user location
def fetch_nearby_doctors(user_lat, user_lng, doctor_type):
    """Fetch nearby doctors using Google Maps Places API."""
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{user_lat},{user_lng}",
        "radius": 5000,  # 5 km radius
        "keyword": doctor_type,
        "type": "doctor",
        "key": google_maps_api_key
    }
    response = requests.get(places_url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error(f"Error fetching nearby doctors: {response.text}")
        return []


# Map disease type to doctor specialization
def get_doctor_specialization(disease):
    """Map disease to a recommended doctor type."""
    disease_mapping = {
        "cardiac": "cardiologist",
        "diabetes": "endocrinologist",
        "orthopedic": "orthopedic doctor",
        "skin": "dermatologist",
        "lungs": "pulmonologist",
        "neurological": "neurologist",
        "general": "general practitioner",
    }
    return disease_mapping.get(disease.lower(), "general practitioner")


# Streamlit App Configuration
st.set_page_config(page_title="AI Medical Insights", page_icon=":hospital:")
st.title("SMART MEDICAL INSIGHTS")
st.subheader("AI-Driven Medical Image Analysis with Personalized Doctor Recommendations")

# Location Input
st.write("Please provide your location for personalized recommendations.")
address = st.text_input("Enter your address or city (e.g., 'New Delhi', '123 Main St, San Francisco')",
                        placeholder="Type your location here")

# File Uploader for Medical Image Upload
upload_file = st.file_uploader("Upload your medical image for analysis", type=["png", "jpg", "jpeg"])

# Button to generate analysis
submit_button = st.button("Generate Analysis and Find Doctors Nearby")

# Process when the submit button is clicked
if submit_button:
    if not address:
        st.error("Please provide your location.")
    elif upload_file is not None:
        # Convert address to latitude and longitude
        user_lat, user_lng = geocode_address(address)
        if user_lat is None or user_lng is None:
            st.error("Could not process location. Please try again.")
        else:
            encoded_image = encode_image_to_base64(upload_file)
            if not encoded_image:
                st.error("Failed to process the image. Please try again.")
            else:
                st.write("Analyzing the uploaded image...")

                # NVIDIA API Call
                api_key = "nvidia_api_key"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }
                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": f'<img src="data:image/jpeg;base64,{encoded_image}" />'
                        }
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.20,
                    "top_p": 0.70,
                    "stream": False
                }
                response = requests.post(nvidia_api_url, headers=headers, json=payload)

                if response.status_code == 200:
                    analysis_result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                    st.subheader("AI-Generated Medical Analysis")
                    st.write(analysis_result)

                    # Mocked disease detection
                    detected_disease = "cardiac"  # Replace with actual NLP-based disease extraction logic
                    st.write(f"**Detected Disease:** {detected_disease}")

                    # Recommendations
                    doctor_type = get_doctor_specialization(detected_disease)
                    st.write(f"**Recommended Specialist:** {doctor_type.capitalize()}")
                    st.write(f"**Precautions:** Stay hydrated, avoid stress, and consult a {doctor_type} immediately.")

                    # Fetch nearby doctors
                    st.write("Finding nearby doctors in your area...")
                    nearby_doctors = fetch_nearby_doctors(user_lat, user_lng, doctor_type)
                    st.subheader("Nearby Doctors")
                    if nearby_doctors:
                        for doctor in nearby_doctors:
                            st.write(f"**{doctor.get('name')}** - {doctor.get('vicinity')}")
                    else:
                        st.write("No doctors found nearby. Please try again later.")
                else:
                    st.error(f"Error in NVIDIA API: {response.text}")
    else:
        st.error("Please upload an image before proceeding.")
