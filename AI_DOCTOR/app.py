from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) #initialize and configure the Google Generative AI client library with an API key stored in an environmental variable

def get_gemini_response(input,image,prompt):
    model=genai.GenerativeModel("gemini-1.5-pro") #initializes the Gemini 1.5 Pro model using the Google Generative AI SDK.
    response=model.generate_content([input,image[0],prompt]) #tries to pass both text(prompt) and image to the model
    return response.text
def input_image_setup(uploaded_file): #converts an uploaded image file into a structured format containing its MIME type and binary data, suitable for sending to an API or processing model.
    if uploaded_file is not None:
        bytes_data=uploaded_file.getvalue() #retrieves the binary data (bytes) from the uploaded file.
        image_parts=[
            {
                "mime_type":uploaded_file.type, #his is the MIME (Multipurpose Internet Mail Extensions) type of the uploaded file
                "data":bytes_data

            }
        ]
        return image_parts  #This can then be passed to the API or the model
    else:
        raise FileNotFoundError("No file uploaded")
input_prompt="""
You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories ,also provide the details of every food items with calories intake
in below format
1.Item 1- no of calories
2.Item 2-no of calories
------
Total Calories: [Total calorie count]
give a rough calculation on portion size estimated from the picture irrespective of the cooking methods
"""
st.set_page_config(page_title="AI Nutritionist App") 
st.header("AI Nutritionist App")
input=st.text_input("Input prompt:",key="input") # Creates a text input field where the user can enter a prompt (e.g., a custom question or instruction)
uploaded_file=st.file_uploader("choose an image..",type=["jpg","jpeg","png"]) #
image=""
if uploaded_file is not None:
    image=Image.open(uploaded_file) # Opens the uploaded image using the Python Imaging Library (PIL).
    st.image(image,caption="uploaded Image.",use_column_width=True) # Displays the uploaded image with the caption "uploaded Image" and adjusts its width to fit the column size.
submit=st.button("Tell me the total calories") # Creates a button labeled "Tell me the total calories".

if submit:
    image_data=input_image_setup(uploaded_file) # Calls the `input_image_setup` function to prepare the uploaded image file for processing, converting it to the necessary format (e.g., bytes).
    response=get_gemini_response(input_prompt,image_data,input) # Calls the `get_gemini_response` function, passing the input prompt, the processed image data, and the custom input prompt to generate the response (likely to calculate the calories in the food items shown in the image).
    st.subheader("The Response is:")
    st.write(response) #  Writes and displays the generated response from the AI model, which contains the nutritional information and calorie counts.