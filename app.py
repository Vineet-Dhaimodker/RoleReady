from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import base64
import io

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,pdf_content,prompt):
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text

def input_pdf_setup(upload_file):
    if upload_file is not None:
        # converting pdf tp image
        if os.getenv("HOME") == "/app":  # Streamlit Cloud environment
            images = convert_from_bytes(upload_file.read())
        else:  # Local environment
            images = convert_from_bytes(upload_file.read(), poppler_path=r'poppler-24.08.0/Library/bin')

        first_page=images[0]

        # convert image to bytes
        image_bytes=io.BytesIO()
        first_page.save(image_bytes, format='JPEG')
        image_bytes =  image_bytes.getvalue()

        pdf_parts=[
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode() #encode to base 64
            }
        ]

        return pdf_parts
    else:
        raise FileNotFoundError("Please upload File!")
    
## Sreamlit app

st.set_page_config(page_title="Role Ready: Personal ATS powered by Google Gemini")
st.header("Application Tracking System")
input_text = st.text_area("Enter your desired job description: ",key="input")
upload_file=st.file_uploader("Upload your Resume PDF",type=["pdf"])

if upload_file is not None:
    st.write("PDF Uploaded")

submit1=st.button("Tell Me About the Resume")
submit2=st.button("Tailor my resume for this job")
submit3=st.button("Generate ATS score(percentage match)")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if upload_file is not None:
        pdf_content=input_pdf_setup(upload_file)
        response=get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload your Resume!")

elif submit3:
    if upload_file is not None:
        pdf_content=input_pdf_setup(upload_file)
        response=get_gemini_response(input_prompt3,pdf_content,input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload your Resume!")
        