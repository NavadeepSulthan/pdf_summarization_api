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
    response = model.generate_content(prompt)
    return response.text.strip()


# Function to format markdown-like syntax into HTML
def format_markdown(text):
    # Convert **...** to <strong>...</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    
    # Process lines: convert lines starting with "* " to bullet list items.
    lines = text.splitlines()
    formatted_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("* "):
            if not in_list:
                formatted_lines.append("<ul>")
                in_list = True
            # Remove the leading "* " and wrap with <li> tag
            formatted_lines.append(f"<li>{stripped[2:].strip()}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            formatted_lines.append(line)
    if in_list:
        formatted_lines.append("</ul>")
    
    # Replace remaining newlines with <br> tags for readability
    return "<br>".join(formatted_lines)


@app.route('/')
def upload_page():
    """Serve the upload page."""
    return render_template("upload.html")


@app.route('/extract_text', methods=['POST'])
def extract_text():
    """Extracts text from a PDF file, summarizes it, applies formatting, and renders an HTML page."""
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files['pdf']
    pdf_path = os.path.join("uploads", pdf_file.filename)
    os.makedirs("uploads", exist_ok=True)
    pdf_file.save(pdf_path)

    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    summary = summarize_text(extracted_text[:125000])  # Limiting input to avoid overload
    
    # Apply custom markdown formatting to preserve original spacing, bolding, and bullets.
    formatted_summary = format_markdown(summary)
    
    return render_template("summary.html", summary=formatted_summary)


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
