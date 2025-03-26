from flask import Flask, request, jsonify
import pdfplumber
import requests

app = Flask(__name__)

# Hugging Face API Details
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HUGGINGFACE_API_TOKEN = "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"  # Replace with your API key
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def summarize_text(text):
    payload = {"inputs": text, "parameters": {"max_length": 150, "min_length": 50, "do_sample": False}}
    response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    else:
        return f"Summarization failed with status code: {response.status_code}"

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

    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    summary = summarize_text(extracted_text)

    return jsonify({"summary": summary})

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
