from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        q = data.get('q', '')
        key = data.get('key', '')
        mode = data.get('level', 'student')
        
        if mode == 'cyber' and "771" not in str(key):
            return jsonify({'response': '❌ الوصول مرفوض: كود التفعيل 771 مطلوب.'})

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a Cyber Security Expert." if mode == 'cyber' else "You are a helpful assistant."},
                {"role": "user", "content": q}
            ]
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        return jsonify({'response': r.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ في السيرفر: {str(e)}'})

if __name__ == '__main__':
    app.run()
