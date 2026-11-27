import fitz
import json
import google.generativeai as genai

# ==========================================
# GEMINI CONFIGURATION
# ==========================================

genai.configure(
    api_key="AQ.Ab8RN6KZ1QZvEQ4ZWEjX1fkQlF8OpGWDqGrNIu4Rs4vscAwsZQ"
)

model = genai.GenerativeModel(
    "gemini-3.5-flash"
)

# ==========================================
# PDF TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(pdf_path):

    text = ""

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()

    return text


# ==========================================
# GEMINI MEDICAL EXTRACTION
# ==========================================

def extract_medical_data(pdf_path):

    report_text = extract_text_from_pdf(pdf_path)

    if not report_text.strip():
        return {
            "error": "No readable text found in PDF"
        }

    prompt = f"""
Extract ONLY these fields from the medical report.

Return valid JSON only.

If a field is missing, return "Not Found".

Fields:
blood_group
hemoglobin
creatinine
egfr
hiv_status
hepatitis_b_status
hepatitis_c_status
hla_a1
hla_a2
hla_b1
hla_b2
hla_dr1
hla_dr2
crossmatch_result
report_date

Medical Report:
{report_text}
"""

    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

    except Exception as e:

        return {
            "error": str(e)
        }

    result = response.text.strip()

    if result.startswith("```json"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    try:

        data = json.loads(result)

        return data

    except json.JSONDecodeError:

        return {
            "error": "Gemini returned invalid JSON",
            "raw_response": result
        }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    pdf_path = "uploads/report.pdf"

    extracted_data = extract_medical_data(pdf_path)

    print(
        json.dumps(
            extracted_data,
            indent=4
        )
    )