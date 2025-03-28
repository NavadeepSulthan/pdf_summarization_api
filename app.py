from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF for PDF extraction
import google.generativeai as genai
import os
import re 
app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyD_fHU2OINK5MwEIOUEgoyj60-JroAk57k"  # Replace with your actual API Key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-002")


# Function to extract text from a PDF
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
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error in AI summarization: {str(e)}"


# Function to format markdown-like syntax into HTML
def format_markdown(text):
    """Convert markdown-like syntax to a readable format."""
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    
    lines = text.splitlines()
    formatted_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("* "):
            if not in_list:
                formatted_lines.append("<ul>")
                in_list = True
            formatted_lines.append(f"<li>{stripped[2:].strip()}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            formatted_lines.append(line)
    if in_list:
        formatted_lines.append("</ul>")

    return "\n".join(formatted_lines)


@app.route('/extract_text', methods=['POST'])
def extract_text():
    """Extracts text from a PDF file, summarizes it, and returns JSON."""
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files['pdf']
    pdf_path = os.path.join("uploads", pdf_file.filename)
    os.makedirs("uploads", exist_ok=True)
    pdf_file.save(pdf_path)

    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    summary = summarize_text(extracted_text[:125000])  # Limiting input size
    
    formatted_summary = format_markdown(summary)
    
    return jsonify({"summary": formatted_summary})  # ✅ Return JSON instead of HTML


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
