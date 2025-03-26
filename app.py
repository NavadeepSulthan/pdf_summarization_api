from flask import Flask, request, jsonify
import pdfplumber
from transformers import pipeline

app = Flask(__name__)

# Load the Hugging Face T5-small model for summarization
summarizer = pipeline("summarization", model="t5-small")

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400
    
    pdf_file = request.files['pdf']
    
    extracted_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    # If no text was extracted
    if not extracted_text.strip():
        return jsonify({"error": "No text found in the PDF"}), 400

    # Summarize extracted text (T5-small has a 512 token limit per input)
    summary = summarizer(extracted_text, max_length=150, min_length=50, do_sample=False)

    return jsonify({"summary": summary[0]['summary_text']})

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
