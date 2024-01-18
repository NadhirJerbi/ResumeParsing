import streamlit as st
from PIL import Image,ImageDraw, ImageOps
import os
import requests
import base64
import io
import tempfile
import fitz
from PIL import Image
import re
import json
from tika import parser
from perplexity import Perplexity
from query import query

def extract_Profile_image(pdf_path, output_image_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    image_list = page.get_images(full=True)

    # Initialize variables to store information about the largest image
    largest_image_width = 0
    largest_image_height = 0
    largest_image_bytes = None

    # Iterate through the images on the page
    for image_index, img in enumerate(image_list):
        xref = img[0]
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]
        image_width = base_image["width"]
        image_height = base_image["height"]

        # Check if the current image is larger than the previous largest image
        if image_width > largest_image_width and image_height > largest_image_height:
            largest_image_width = image_width
            largest_image_height = image_height
            largest_image_bytes = image_bytes

    if largest_image_bytes:
        # Save the largest image to a file
        image_file = open(output_image_path, "wb")
        image_file.write(largest_image_bytes)
        image_file.close()
        return output_image_path
    else:
        return convert_pdf2img(pdf_path,output_image_path)

    # Close the PDF
    pdf_document.close()

def conver2pdf(file,fileName):
    instructions = {'parts': [{'file': 'document'}]}
    response = requests.request('POST',
      'https://api.pspdfkit.com/build',
      headers = {'Authorization': 'Bearer pdf_live_rr7Ivtg4hxUPAx3Qr2QtxlBnFl3HtSl8Kyc4R5lt9nw'},
      files = {'document': file},
      data = {'instructions': json.dumps(instructions)},
      stream = True)
    if response.ok:
        with open(f'./resume/pdf/{fileName}.pdf', 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8096):
                fd.write(chunk)
        return(open(f'./resume/pdf/{fileName}.pdf','rb'))
    else:
      print(response.text)
      exit()


def convert_pdf2img(pdfPath,imagePath):
    # Open the PDF file
    pdf=fitz.open(pdfPath)
    # Get the pixmap of the first page of the PDF
    pixImage = pdf[0].get_pixmap()
    # Save the pixmap as an image file
    pixImage.save(imagePath)
    # Return the path to the saved image file
    return imagePath


def saveFile(file,fileName):
        
        fname = fileName.split(".")[0]
        pathImg=f'./resume/img/{fname}.jpg'
        pathPdf=f'./resume/pdf/{fileName}.pdf'
        
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(file.read())
        temp_file_path = temp_file.name
        fitz.open(temp_file_path).save(pathPdf)
        resumeImg = extract_Profile_image(pathPdf,pathImg)
        temp_file.close()
        return pathPdf,pathImg
    
def extract_json_from_text(text):
    start_index = text.find('{')
    end_index = text.rfind('}')
    json_text = text[start_index:end_index + 1]
    json_text = json_text.strip('`\n').replace('\\n', '\n')
    try:
        json_data = json.loads(json_text)
        return json_data
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return None
    
def extract_text_from_pdf(pdf_path):
    raw_text = ""
    
    try:
        parsed_pdf = parser.from_file(pdf_path)
        raw_text = parsed_pdf.get('content', '')
    except Exception as e:
        print(f"Error extracting text: {e}")
    return re.sub(r"\s+", " ", raw_text).strip() 

def remove_empty_fields(obj):
    if isinstance(obj, dict):
        return {k: remove_empty_fields(v) for k, v in obj.items() if v is not None and remove_empty_fields(v)}
    elif isinstance(obj, list):
        return [remove_empty_fields(item) for item in obj if item is not None and remove_empty_fields(item)]
    else:
        return obj   

perplexity = Perplexity()
def fnDectec(file):
        filesSections=[]
        fileName = (file.name).split(".")[0]
        # Check if the file extension is one of the allowed formats
        if file.name.endswith((".docx", ".pdf", ".doc", ".xlsx", ".xls", ".pptx", ".ppt")):
            if not file.name.endswith((".pdf")):
                # Convert the file to PDF if it's not already in PDF format
                file = conver2pdf(file,fileName)
            # Save the file to a specific path and obtain the paths to the PDF and image versions   
            pathPdf,pathImg=saveFile(file,fileName)
            resume = extract_text_from_pdf(pathPdf)
            # Make a query
            query1 = "Convert this resume `"+resume+query
            resumeJson=None
            while resumeJson==None :
                answer = perplexity.search(query1)
                # Print the answer
                for a in answer:
                    result=a['answer']
                print(result)
                # Close the Perplexity object
                resumeJson = extract_json_from_text(result)
                print(resumeJson)
            with open(f'./resume/json/{fileName}.json', 'w') as json_file:
                json.dump(resumeJson, json_file, indent=2)
            data = {"resumeJson":resumeJson, "path":{"pathImg":pathImg,"pathPDF":pathPdf,}}
            filesSections.append(data)
        else:
            print(file + " is not a valid file.") 
        return filesSections

   
######################################## StreamLit App ########################################


def main():
    
    st.sidebar.title("📤 Upload your Resumes")
    with st.sidebar :
        resume_files = st.file_uploader(
        " ", type=[".docx", ".pdf", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"],accept_multiple_files=True)
    
    st.title("📑 Resume parsing using  Perplexity AI 🤖 ")
    st.subheader("""This miniature application is designed to convert resumes in various formats (DOCX, PDF, DOC, XLSX, XLS, PPTX, PPT) into JSON format. It offers the following features:
    *Conversion of one or multiple resumes
    *Preview of resumes and their corresponding JSON parsing
    *Download of individual resume JSON or a consolidated array of JSON
The parsing functionality utilizes the Perplexity AI Python library.""")
    if resume_files :
        Mtab1, Mtab2 = st.tabs(["🕵🏻 Parsing Details","⬇️ Download"])
        allResume=[]
        with Mtab1:
            # Iterate over the uploaded resumes
            for resume in resume_files:
                with resume:
                    # Create a dictionary for the resume data
                    col1,col2,col3=st.columns(3)  
                    with col2 :
                        with st.spinner(text=f"Detecting...{resume.name}"):
                            response = fnDectec(resume)
                            resumeJson=response[0]['resumeJson']
                            imgPathsJson=response[0]['path']
                            allResume.append({'resume':resume.name,'content':resumeJson})
                            x=None                                    
                    
                    with st.expander(f" 🗃️ More details  {resume.name} ", expanded=False):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            profile_image = Image.open(imgPathsJson['pathImg'])  # Add your profile picture
                                                        
                            # Recadrer l'image en un carré
                            size = min(profile_image.size)
                            profile_image = ImageOps.fit(profile_image, (size, size))
                            
                            # Créer un masque circulaire
                            mask = Image.new("L", (size, size), 0)
                            draw = ImageDraw.Draw(mask)
                            draw.ellipse((0, 0, size, size), fill=255)
                            
                            # Appliquer le masque à l'image de profil
                            profile_image.putalpha(mask)
                            
                            # Afficher l'image de profil dans un cercle
                            st.image(profile_image, width=100,use_column_width=True)
                            
                        with col2:
                            if 'Name' in resumeJson:
                                st.title(resumeJson['Name'].replace("\n", ""))
                            if 'Job_title' in resumeJson :
                                st.subheader(resumeJson['Job_title'].replace("\n", " "))
                        tab3, tab2 = st.tabs(["📋 Resume PDF", " 💾 Resume Json Content"])

                        with tab2:
                            # Convert the JSON object to a string
                            json_data = json.dumps(resumeJson)

                            # Create a download button
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f'{resume.name}.json',
                                mime="application/json"
                            )
                            tab2.write(json.loads(json.dumps(remove_empty_fields(resumeJson), indent=2)))
                        with tab3:
                        # Read file as bytes:
                            with open(imgPathsJson['pathPDF'], "rb") as file:
                                pdf_bytes = io.BytesIO(file.read())

                            bytes_data = pdf_bytes.getvalue()

                            # Convert to utf-8
                            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')

                            # Embed PDF in HTML
                            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

                            # Display file
                            st.markdown(pdf_display, unsafe_allow_html=True)
        with Mtab2:
            # Convert the JSON object to a string
            json_data = json.dumps(allResume)

            # Create a download button
            st.download_button(
                    label="Download All",
                    data=json_data,
                    file_name='AllResume.json',
                    mime="application/json"
                    )
              
                                



if __name__ == '__main__':
    st.set_page_config(page_title="Resume Parsing", page_icon="📖", layout="wide")
    # Define color scheme
    primary_color = "#f0f2f6"
    secondary_color = "#f0f2f6"
    third_color = "#ff2a23"

    # Global styles
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #ffffff;
            color: {third_color};
            font-family: 'Arial', sans-serif;
        }}
        .stMarkdown p {{
            font-size: 16px;
            line-height: 1.6;
        }}
        .stHeader {{
            color: {third_color};
        }}
        .stMetricValue {{
            font-size: 24px;
            color: #0a21ad
        }}
        .stPlotlyChart .plotly .modebar {{
            background-color: transparent;
        }}
        .stTabs .plotly .modebar {{
            background-color: {secondary_color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    main()