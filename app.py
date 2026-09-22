import os
import io

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load API
load_dotenv()
API_KEY = os.environ.get('Gemini_api_key')

# Page configuration
st.set_page_config(page_title="AI Scanner", layout="wide")

client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else: 
    st.error("Gemini_api_key is not set. Add it to a .env file or your environment variables.")

st.title("AI Document and Receipt Scanner")
st.write("Upload a photo of a receipt or handwritten note and watch the AI organize it.")

left_col, right_col = st.columns([1,1])

AI_PROMPT = """
You are a help assistant. Look at this image of a receipt or not.
Make a clean markdown table of all the items, quantities, etc
If there are any handwritten, do best to read it!.
"""

FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png"
}

image_byte = None
mime_type = None

with left_col:
    st.subheader("Upload photo")
    uploaded_file = st.file_uploader("Drop your image receipt here...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="your uploaded document", width=400)

        save_format = image.format if image.format in FORMAT_TO_MIME else "JPEG"
        mime_type = FORMAT_TO_MIME[save_format]

        img_byte_arr = io.BytesIO()
        # convert to RGB first: PNGs with transparency can fail to save as JPEG
        if save_format == "JPEG" and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(img_byte_arr, format = save_format)
        image_byte = img_byte_arr.getvalue()

with right_col:
    st.subheader("Organized Data")

    if uploaded_file is not None:
        if st.button("Let AI Read It!:", type = "primary", disabled=client is None):
            with st.spinner("AI is thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            types.Part.from_bytes(data=image_byte, mime_type=mime_type),
                            AI_PROMPT,
                        ],
                    )
                    st.success("Done!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Something went wrong {e}")
    else:
        st.info("Waiting for you to upload an image on the left.")

                