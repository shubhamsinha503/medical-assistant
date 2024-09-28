import streamlit as st
import requests
import base64

# NVIDIA API endpoint
invoke_url = "https://ai.api.nvidia.com/v1/vlm/nvidia/vila"

# Stream or non-stream response (False by default for full response)
stream = False

# Function to encode the uploaded image to base64
def encode_image_to_base64(file):
    """Encode the uploaded image to base64 format."""
    return base64.b64encode(file.read()).decode()

# Streamlit App Configuration
st.set_page_config(page_title="VitalImage Analysis", page_icon=":robot:")
st.title("SMART MEDICAL INSIGHTS")
st.subheader("Navigate through internal medical conditions using AI-driven image analysis.")
st.image("7191136_3568984.jpg", width=300)

# File Uploader for Medical Image Upload
upload_file = st.file_uploader("Upload your medical image for analysis", type=["png", "jpg", "jpeg"])

# Button to generate analysis
submit_button = st.button("Generate the analysis")

# Logic for handling file upload and analysis generation
if submit_button:
    if upload_file is not None:
        # Ensure the uploaded file is within the size limit (base64 encoding shouldn't exceed 180k characters)
        encoded_image = encode_image_to_base64(upload_file)
        assert len(encoded_image) < 180_000, "Image size too large. Use the assets API to upload larger images."

        st.write("File uploaded and processed for analysis...")

        # API key provided directly
        api_key = "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"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream" if stream else "application/json"
        }

        # Define the custom medical prompt
        custom_prompt = f"""
        Act as a world-class medical practitioner specializing in image analysis. 
        Given the following context, criteria, and instructions, perform a detailed analysis of the medical image with a strong focus on identifying abnormalities.

        ## Context
        The task involves examining a set of medical images (e.g., X-rays, MRIs, CT scans) to detect any abnormalities or signs of disease. The analysis aims to provide a comprehensive report on the findings and suggest appropriate next steps for patient care.

        ## Approach
        1. **Detailed Analysis**: Carefully analyze the provided medical image, looking for unusual patterns, lesions, or other indicators of abnormalities.
        2. **Findings Report**: Document all observed anomalies or signs of disease in a clear and concise manner, using medical terminology suitable for healthcare professionals.
        3. **Recommendations and Next Steps**: Following the findings, propose potential next steps, such as further diagnostic tests or referrals to specialists.
        4. **Treatment Suggestions**: If applicable, recommend possible treatment options or interventions based on the identified findings.

        ## Response Format
        Utilize a structured report format including:
        1. **Image Identification**: Reference the image by its designation.
        2. **Findings**: List the abnormalities noted for the image.
        3. **Recommendations**: Outline the suggested next steps following the analysis.
        4. **Treatment Options**: Present possible treatments with any relevant medical guidelines or evidence.

        ## Instructions
        - Ensure clarity and precision in language while articulating the findings and recommendations.
        - Maintain a professional tone suitable for medical communications.
        - Be thorough in documenting all findings to support clinical decision-making.
        - Avoid speculation; base all analyses on observable evidence in the images provided.
        <img src="data:image/png;base64,{encoded_image}" />
        """

        # Define the payload with the base64-encoded image and custom prompt
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": custom_prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.20,
            "top_p": 0.70,
            "seed": 50,
            "stream": stream,  # Stream flag
        }

        # Send POST request to the NVIDIA API
        response = requests.post(invoke_url, headers=headers, json=payload)

        # Process the response
        if stream:
            # If streaming is enabled, iterate over the response lines
            for line in response.iter_lines():
                if line:
                    st.write(line.decode("utf-8"))
        else:
            # If not streaming, extract and display the plain text content
            response_json = response.json()
            content = response_json['choices'][0]['message']['content']
            st.subheader("AI-Generated Analysis")
            st.write(content)

    else:
        st.error("Please upload a medical image before generating the analysis.")

