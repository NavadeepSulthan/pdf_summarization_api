from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HUGGINGFACE_API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/t5-small"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400
    
    pdf_file = request.files['pdf']
    extracted_text = ""

    try:
        import pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"
    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500

    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    # 🔹 Send extracted text to Hugging Face for summarization
    payload = {"inputs": f"summarize: {extracted_text[:3000]}"}  # Limiting text size
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Summarization failed", "details": response.json()}), 500

    summary = response.json()[0]['generated_text']

    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
