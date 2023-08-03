import streamlit as st
import os
import io
from google.cloud import vision
from pdf2image import convert_from_bytes
import json


def extract_text_from_pdf(file):
    """Extracts the text from a PDF file using the Google Vision API."""

    # Get the JSON key from the secrets manager
    json_key = st.secrets["GOOGLE_CLOUD_VISION_JSON_KEY"]

    # Write the JSON key to a temporary file
    json_key_file = "/tmp/json_key.json"
    with open(json_key_file, "w") as f:
        json.dump(json_key, f)

    # Set the environment variable for the Vision client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_file

    # Create a Vision client
    client = vision.ImageAnnotatorClient()

    # Convert the PDF file to images
    images = convert_from_bytes(file.read())

    # Initialize a variable to hold the text
    text = ""

    # Loop over the images and extract the text
    for image in images:
        image.save("output.jpg", "JPEG")
        with io.open("output.jpg", "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        text += response.text_annotations[0].description

    return text

def main():
    """Creates a Streamlit web app that receives a PDF and returns the text in the PDF."""

    # Create a file uploader
    file_input = st.file_uploader("Upload a PDF file", type=['pdf'])

    # If a PDF file is uploaded, extract the text and display it
    if file_input is not None:
        text = extract_text_from_pdf(file_input)
        st.write(text)

if __name__ == "__main__":
    main()
