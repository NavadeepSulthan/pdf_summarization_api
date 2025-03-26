from flask import Flask, request, jsonify
import pdfplumber
from transformers import pipeline

app = Flask(__name__)

# Load the summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/extract_text', methods=['POST'])
def extract_and_summarize_text():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400
    
    pdf_file = request.files['pdf']
    
    extracted_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    
    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    # Summarize text (limit per model constraints)
    max_input_length = 1024
    summarized_text = ""
    
    # Split text if it's too long
    for i in range(0, len(extracted_text), max_input_length):
        chunk = extracted_text[i:i+max_input_length]
        summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
        summarized_text += summary[0]['summary_text'] + " "

    return jsonify({"summary": summarized_text.strip()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
