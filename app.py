from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF for PDF extraction
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyD_fHU2OINK5MwEIOUEgoyj60-JroAk57k"  # Replace with your actual API Key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-002")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)  # Open PDF
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
    return text

# Function to summarize text using Gemini AI
def summarize_text(text):
    prompt = f"""
    Summarize the following text concisely while keeping key concepts.
    Include the most important points and generate at least 30 minutes of reading content.
    Ensure the summary is easy to understand.
    
    {text}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

@app.route('/')
def upload_page():
    """Serve the upload page."""
    return render_template("upload.html")

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """Extracts text from a PDF file, summarizes it, and renders a UI-friendly HTML page."""
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files['pdf']
    pdf_path = os.path.join("uploads", pdf_file.filename)
    os.makedirs("uploads", exist_ok=True)
    pdf_file.save(pdf_path)

    extracted_text = extract_text_from_pdf(pdf_path)

    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    # Limit input length to avoid API overload (if necessary)
    summary = summarize_text(extracted_text[:125000])
    
    # Assume summary is returned as a JSON-like text (even if it's a string, we treat it as the summary)
    # Convert newlines to <br> to preserve formatting in HTML
    formatted_summary = summary.replace("\n", "<br>")
    
    return render_template("summary.html", summary=formatted_summary)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
