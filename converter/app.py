# from flask import Flask, render_template, request, send_file
# import pymupdf as fitz  # PyMuPDF
# import os
# import pandas as pd
# import json
# from PIL import Image

# app = Flask(__name__)

# # Define folders for uploads and conversions
# UPLOAD_FOLDER = "uploads"
# CONVERTED_FOLDER = "converted"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER

# #@app.route('/')
# #def index():
# #    print("index route accessed")
# #    return render_template('index.html')

# if __name__ == "__main__":
#     app.run(debug=True)

# def pdf_converter(input_pdf):
#     if not os.path.exists(input_pdf):
#         print("Error: File not found! Please check the file path.")
#         return
    
#     try:
#         doc = fitz.open(input_pdf)
#     except Exception as e:
#         print(f"Error opening PDF: {e}")
#         return
    
#     print("Choose conversion type:")
#     print("1. PDF to Text")
#     print("2. PDF to Images")
#     print("3. PDF to JSON")
#     print("4. PDF to CSV")
#     choice = input("Enter your choice (1/2/3/4): ")
    
#     try:
#         if choice == "1":  # PDF to Text
#             text = "".join([page.get_text("text") for page in doc])
#             if not text.strip():
#                 print("Warning: No extractable text found in the PDF!")
#             output_txt = input_pdf.replace(".pdf", ".txt")
#             with open(output_txt, "w", encoding="utf-8") as f:
#                 f.write(text)
#             print(f"PDF converted to Text: {output_txt}")

#         elif choice == "2":  # PDF to Images
#             output_folder = input_pdf.replace(".pdf", "_images")
#             os.makedirs(output_folder, exist_ok=True)
#             for i, page in enumerate(doc):
#                 image = page.get_pixmap()
#                 img_path = os.path.join(output_folder, f"page_{i+1}.png")
#                 image.save(img_path)
#             print(f"PDF pages saved as images in: {output_folder}")

#         elif choice == "3":  # PDF to JSON
#             data = {"pages": [{"page_number": i+1, "text": page.get_text("text")} for i, page in enumerate(doc)]}
#             output_json = input_pdf.replace(".pdf", ".json")
#             with open(output_json, "w", encoding="utf-8") as f:
#                 json.dump(data, f, indent=4)
#             print(f"PDF converted to JSON : {output_json}")

#         elif choice == "4":  # PDF to CSV
#             tables = [[i+1, page.get_text("text")] for i, page in enumerate(doc)]
#             df = pd.DataFrame(tables, columns=["Page Number", "Text Content"])
#             output_csv = input_pdf.replace(".pdf", ".csv")
#             df.to_csv(output_csv, index=False)
#             print(f"PDF converted to CSV: {output_csv}")

#         else:
#             print("Invalid choice. Please enter 1, 2, 3, or 4.")
#     except PermissionError:
#         print("Error: Permission denied! Check file write permissions.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Example Usage
# if __name__ == "__main__":
#     input_pdf = input("Enter the PDF file path: ")
#     pdf_converter(input_pdf)

from flask import Flask, render_template, request, send_file, redirect, url_for
import fitz  # PyMuPDF
import os
import pandas as pd
import json
import zipfile
import shutil
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.secret_key = 'your-secret-key-here'

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'pdfFile' not in request.files:
        return redirect(request.url)
    
    file = request.files['pdfFile']
    conversion_type = request.form['conversionType']
    
    if file.filename == '':
        return redirect(request.url)
    
    if not file or not allowed_file(file.filename):
        return "Invalid file type. Only PDF files are allowed.", 400
    
    try:
        # Secure filename and create input path
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Process conversion based on type
        if conversion_type == 'text':
            output = pdf_to_text(input_path)
            return send_file(
                output,
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}.txt",
                mimetype='text/plain'
            )
        elif conversion_type == 'images':
            zip_buffer = pdf_to_images(input_path)
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}_images.zip",
                mimetype='application/zip'
            )
        elif conversion_type == 'json':
            output = pdf_to_json(input_path)
            return send_file(
                output,
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}.json",
                mimetype='application/json'
            )
        elif conversion_type == 'csv':
            output = pdf_to_csv(input_path)
            return send_file(
                output,
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}.csv",
                mimetype='text/csv'
            )
        else:
            return "Invalid conversion type selected.", 400
            
    except Exception as e:
        return f"Conversion failed: {str(e)}", 500
    finally:
        # Clean up uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)

def pdf_to_text(input_path):
    doc = fitz.open(input_path)
    text = "\n".join([page.get_text() for page in doc])
    
    # Create in-memory file
    output = BytesIO()
    output.write(text.encode('utf-8'))
    output.seek(0)
    return output

def pdf_to_images(input_path):
    doc = fitz.open(input_path)
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_data = pix.tobytes()
            zip_file.writestr(f"page_{i+1}.png", img_data)
    
    zip_buffer.seek(0)
    return zip_buffer

def pdf_to_json(input_path):
    doc = fitz.open(input_path)
    data = {
        "metadata": {
            "pages": len(doc),
            "author": doc.metadata.get('author', ''),
            "title": doc.metadata.get('title', '')
        },
        "pages": [
            {
                "page_number": i+1,
                "text": page.get_text()
            } for i, page in enumerate(doc)
        ]
    }
    
    output = BytesIO()
    output.write(json.dumps(data, indent=2).encode('utf-8'))
    output.seek(0)
    return output

def pdf_to_csv(input_path):
    doc = fitz.open(input_path)
    data = [{
        "Page Number": i+1,
        "Text": page.get_text()
    } for i, page in enumerate(doc)]
    
    output = BytesIO()
    df = pd.DataFrame(data)
    df.to_csv(output, index=False)
    output.seek(0)
    return output

if __name__ == '__main__':
    app.run(debug=True)