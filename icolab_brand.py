from flask import Flask, request, jsonify
import os
import openai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/brand', methods=['POST'])
def analyze_brand():
    data = request.json
    brand_url = data.get("website")
    
    if not brand_url:
        return jsonify({"error": "Website is required"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise brand strategist. Return only one short sentence summary about the brand, suitable for a chat UI."
                },
                {
                    "role": "user",
                    "content": f"Summarize the brand based on its homepage: {brand_url}"
                }
            ],
            temperature=0.7,
            max_tokens=50  # adjust as needed
        )
        
        output = response.choices[0].message.content.strip()
        print("✅ GPT Response:", output)
        return jsonify({"reply": output}), 200

    except Exception as e:
        print("❌ GPT Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
