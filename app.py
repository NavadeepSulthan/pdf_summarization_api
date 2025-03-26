from flask import Flask, request, jsonify
import requests
import pdfplumber

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
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"
    except Exception as e:
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    # Prepare data for Hugging Face API
    payload = {"inputs": f"summarize: {extracted_text[:3000]}"}

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response_data = response.json()

        print("Hugging Face Response:", response_data)  # Debugging

        # Handle different response formats
        if isinstance(response_data, list) and "generated_text" in response_data[0]:
            summary = response_data[0]["generated_text"]
        elif isinstance(response_data, dict) and "summary_text" in response_data:
            summary = response_data["summary_text"]
        else:
            return jsonify({"error": "Summarization API returned an unexpected response", "details": response_data}), 500

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
