import re
import pdfplumber

# Function to Extract Phone, Fax, and Email
def extract_phone_fax_email(text):
    phone_pattern = r"\b\d{10}\b"  # Extracts a 10-digit phone number
    fax_pattern = r"F\s?ax:\s*([\d\-\s]+)"  # Handles "F ax" issue
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  # Extracts emails

    phone = re.search(phone_pattern, text)
    fax = re.search(fax_pattern, text)
    email = re.search(email_pattern, text)

    return (
        phone.group() if phone else "N/A",
        fax.group(1) if fax else "N/A",  # Capture first group in fax regex
        email.group() if email else "N/A"
    )

# Function to Extract Data from PDF
def extract_pdf_data(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                phone, fax, email = extract_phone_fax_email(text)  # Extract phone, fax, and email
                data = {
                    "Company Name (Respondent)": re.search(r"COMPANY NAME \(RESPONDENT\):\s*(.+)", text),
                    "Customer Reference Company Name": re.search(r"Customer Reference Company Name:\s*(.+)", text),
                    "Customer Reference Contact Person and Title": re.search(r"Customer Reference Contact Person and Title:\s*(.+)", text),
                    "Customer Reference Role": re.search(r"Customer Reference Role.*?:\s*(.+)", text),
                    "Customer Reference Contact Address": re.search(r"Customer Reference Contact Address:\s*(.+)", text),
                    "Telephone Number": phone,  # Extracted phone
                    "F ax": fax,  # Fixed Fax issue
                    "E-mail": email,  # Extracted email
                    "Start Date": re.search(r"Start:\s*([\d/]+)", text),
                    "End Date": re.search(r"E\s?n\s?d:\s*([\d/]+)", text),  # Handles "En d"
                    "Total Amount of Project": re.search(r"T\s?otal Amount of Project:\s*\$?([\d,]+)", text),  # Handles "T otal"
                }
                # Update the data dictionary, ensuring that matches are processed properly
                extracted_data.append({
                    key: match.group(1).strip() if isinstance(match, re.Match) else match
                    for key, match in data.items()
                })
    return extracted_data
