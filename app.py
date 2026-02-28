from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)

# الآن يقرأ المفتاح من إعدادات السيرفر (Environment Variable)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        query = data.get('q')
        level = data.get('level', 'student')
        
        if not GROQ_API_KEY:
            return jsonify({'response': '⚠️ خطأ: المفتاح غير معرف في السيرفر.'})

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        system_msg = "You are TAY CORE AI v6.0. Mode: Student."
        if level == 'cyber':
            system_msg = "You are TAY CORE AI v6.0. Mode: Cybersecurity Expert."

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": query}
            ]
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return jsonify({'response': r.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({'response': f'❌ خطأ في النظام: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
