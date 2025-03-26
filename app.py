from flask import Flask, request, render_template_string
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

@app.route("/", methods=["GET"])
def upload_form():
    """Returns an HTML form to upload a PDF."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Summarizer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            h1 { color: #333; }
            form { margin: 20px auto; padding: 20px; border: 2px solid #ddd; width: 50%; background-color: #f9f9f9; border-radius: 10px; }
            button { padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .container { max-width: 800px; margin: auto; text-align: left; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
        </style>
    </head>
    <body>
        <h1>Upload a PDF to Summarize</h1>
        <form action="/extract_text" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf" required>
            <button type="submit">Summarize PDF</button>
        </form>
    </body>
    </html>
    """)

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """Extracts text from a PDF file and summarizes it."""
    if 'pdf' not in request.files:
        return "<h2 style='color: red;'>Error: No PDF file uploaded</h2>", 400

    pdf_file = request.files['pdf']
    extracted_text = ""

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        return f"<h2 style='color: red;'>Text extraction failed: {str(e)}</h2>", 500

    if not extracted_text.strip():
        return "<h2 style='color: red;'>No text extracted from PDF</h2>", 400

    summary = summarize_text(extracted_text)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Summary</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            h1, h2 { color: #333; }
            .container { max-width: 800px; margin: auto; text-align: left; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
            a { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007BFF; color: white; text-decoration: none; border-radius: 5px; }
            a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>PDF Summary</h1>
        <div class="container">
            <h2>Summarized Text:</h2>
            <pre>{{ summary }}</pre>
        </div>
    </body>
    </html>
    """, summary=summary)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
