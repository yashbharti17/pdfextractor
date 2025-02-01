from flask import Flask, request, render_template, jsonify
import pdfplumber
import re
import requests
from io import BytesIO

app = Flask(__name__)

# Google Apps Script Web App URL
GOOGLE_SHEET_API_URL = "https://script.google.com/macros/s/AKfycbztHWQlH7aB2Y93DINeRAZQx80dy3-dNZV-0Fj9lt2DJyMmMMe-CNXfujqWiL_CHRN6/exec"

# Function to Extract Phone, Fax, and Email
def extract_phone_fax_email(text):
    phone_pattern = r"\b\d{10}\b"
    fax_pattern = r"F\s?ax:\s*([\d\-\s]+)"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    phone = re.search(phone_pattern, text)
    fax = re.search(fax_pattern, text)
    email = re.search(email_pattern, text)

    return (
        phone.group() if phone else "N/A",
        fax.group(1) if fax else "N/A",
        email.group() if email else "N/A"
    )

# Function to Extract Data from PDF
def extract_pdf_data(pdf_file):
    extracted_data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                phone, fax, email = extract_phone_fax_email(text)
                data = {
                    "Company Name (Respondent)": re.search(r"COMPANY NAME \(RESPONDENT\):\s*(.+)", text),
                    "Customer Reference Company Name": re.search(r"Customer Reference Company Name:\s*(.+)", text),
                    "Customer Reference Contact Person and Title": re.search(r"Customer Reference Contact Person and Title:\s*(.+)", text),
                    "Customer Reference Role": re.search(r"Customer Reference Role.*?:\s*(.+)", text),
                    "Customer Reference Contact Address": re.search(r"Customer Reference Contact Address:\s*(.+)", text),
                    "Telephone Number": phone,
                    "Fax": fax,
                    "E-mail": email,
                    "Start Date": re.search(r"Start:\s*([\d/]+)", text),
                    "End Date": re.search(r"E\s?n\s?d:\s*([\d/]+)", text),
                    "Total Amount of Project": re.search(r"T\s?otal Amount of Project:\s*\$?([\d,]+)", text),
                }

                extracted_data.append({
                    key: match.group(1).strip() if isinstance(match, re.Match) else match
                    for key, match in data.items()
                })
    return extracted_data

# Route to Upload PDF and Append to Google Sheets
@app.route("/", methods=["GET", "POST"])
def index():
    extracted_data = None
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        # Read the uploaded file directly from memory
        file_stream = BytesIO(file.read())

        # Extract data
        extracted_data = extract_pdf_data(file_stream)

        # Send data to Google Sheets
        if extracted_data:
            response = requests.post(GOOGLE_SHEET_API_URL, json=extracted_data)
            print("Google Sheets Response:", response.json())

    return render_template("index.html", data=extracted_data)

if __name__ == "__main__":
    app.run(debug=True)
