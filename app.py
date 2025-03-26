from flask import Flask, request, jsonify
import pdfplumber
import requests
import textwrap

app = Flask(__name__)

# Hugging Face API Details
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HUGGINGFACE_API_TOKEN = "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"  # Replace with your API key
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def summarize_text(text):
    """Splits text into chunks & summarizes each separately."""
    chunk_size = 500  # Set chunk size (model limit is ~1024 tokens)
    text_chunks = textwrap.wrap(text, chunk_size)

    summarized_text = ""
    for chunk in text_chunks:
        payload = {"inputs": chunk, "parameters": {"max_length": 200, "min_length": 50, "do_sample": False}}
        response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200 and "summary_text" in response.json()[0]:
            summarized_text += response.json()[0]["summary_text"] + " "
        else:
            summarized_text += "[Error summarizing this section] "

    return summarized_text.strip()

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """Extracts text from a PDF file and summarizes it."""
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files['pdf']
    extracted_text = ""

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

    if not extracted_text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

    summary = summarize_text(extracted_text)

    return jsonify({"summary": summary})

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
